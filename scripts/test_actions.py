#!/usr/bin/env python3
# 轻量动作回归测试：连接后端 WS，逐条下发预设动作到 master（或指定目标）
# 用法：
#   python scripts/test_actions.py ws://127.0.0.1:8765 --target master-01 --side right --delay 2
#   python scripts/test_actions.py ws://192.168.31.170:8765 --only wave,raise_hand_left
#
# 依赖：pip install websockets

import argparse
import asyncio
import json
import time
from typing import Iterable

import websockets

# 官方/项目内预设动作映射（含左右侧 area_id）
PRESET_DEFS = {
    "wave": {"name": "wave", "motion_id": 1002, "area_id": 2, "label": "右手挥手", "side": "right"},
    "wave_left": {"name": "wave_left", "motion_id": 1002, "area_id": 1, "label": "左手挥手", "side": "left"},
    "handshake": {"name": "handshake", "motion_id": 1003, "area_id": 2, "label": "右手握手", "side": "right"},
    "handshake_left": {"name": "handshake_left", "motion_id": 1003, "area_id": 1, "label": "左手握手", "side": "left"},
    "raise_hand": {"name": "raise_hand", "motion_id": 1001, "area_id": 2, "label": "右手举手", "side": "right"},
    "raise_hand_left": {"name": "raise_hand_left", "motion_id": 1001, "area_id": 1, "label": "左手举手", "side": "left"},
    "kiss": {"name": "kiss", "motion_id": 1004, "area_id": 2, "label": "右手飞吻", "side": "right"},
    "kiss_left": {"name": "kiss_left", "motion_id": 1004, "area_id": 1, "label": "左手飞吻", "side": "left"},
    "salute": {"name": "salute", "motion_id": 1013, "area_id": 2, "label": "右手敬礼", "side": "right"},
    "salute_left": {"name": "salute_left", "motion_id": 1013, "area_id": 1, "label": "左手敬礼", "side": "left"},
    "clap": {"name": "clap", "motion_id": 3017, "area_id": 11, "label": "鼓掌", "side": "both"},
    "cheer": {"name": "cheer", "motion_id": 3011, "area_id": 11, "label": "加油", "side": "both"},
    "bow": {"name": "bow", "motion_id": 3001, "area_id": 11, "label": "鞠躬", "side": "both"},
    "dance": {"name": "dance", "motion_id": 3007, "area_id": 11, "label": "动感光波", "side": "both"},
}


def filter_presets(side: str | None, only: Iterable[str] | None) -> list[dict]:
    presets = list(PRESET_DEFS.values())
    if side:
        presets = [p for p in presets if p["side"] in (side, "both")]
    if only:
        only_set = {x.strip() for x in only if x.strip()}
        presets = [p for p in presets if p["name"] in only_set]
    return presets


async def send_actions(ws_url: str, target: str, side: str | None, only: Iterable[str] | None, delay: float):
    rid = f"tester-{int(time.time())}"
    presets = filter_presets(side, only)
    if not presets:
        print("[test] 没有可用动作，检查 --side / --only 参数")
        return

    async with websockets.connect(ws_url, ping_interval=None) as ws:
        hello = {
            "type": "hello",
            "robot_id": rid,
            "role": "controller",
            "config_version": 0,
            "ts": time.time(),
        }
        await ws.send(json.dumps(hello))
        print(f"[test] 已连接 {ws_url}，将发送 {len(presets)} 个动作到 {target}")

        async def recv_loop():
            try:
                async for msg in ws:
                    try:
                        obj = json.loads(msg)
                    except Exception:
                        print("[recv] 非 JSON", msg)
                        continue
                    t = obj.get("type")
                    if t in ("result", "status", "ai_result"):
                        print(f"[recv] {t}: {obj}")
            except Exception as exc:
                print(f"[recv] 结束: {exc}")

        recv_task = asyncio.create_task(recv_loop())

        for item in presets:
            payload = {
                "action": "preset.run",
                "name": item["name"],
                "motion_id": item["motion_id"],
                "area_id": item["area_id"],
                "label": item["label"],
            }
            frame = {
                "type": "exec",
                "robot_id": rid,
                "role": "controller",
                "target_robot": target,
                "payload": payload,
                "ts": time.time(),
            }
            print(f"[send] {item['label']} ({item['name']}) -> {target}")
            await ws.send(json.dumps(frame, ensure_ascii=False))
            await asyncio.sleep(delay)

        await asyncio.sleep(1.0)
        recv_task.cancel()


def main():
    parser = argparse.ArgumentParser(description="按预设动作序列测试 master/slave 动作执行")
    parser.add_argument("ws_url", help="后端 WebSocket 地址，例如 ws://127.0.0.1:8765")
    parser.add_argument("--target", default="master-01", help="目标机器人 ID，默认 master-01")
    parser.add_argument("--side", choices=["left", "right", "both"], help="只测某侧/双侧动作")
    parser.add_argument("--only", help="仅测试指定动作名，逗号分隔，例如 wave,raise_hand_left")
    parser.add_argument("--delay", type=float, default=1.5, help="两条动作之间的间隔秒数")
    args = parser.parse_args()

    only_list = args.only.split(",") if args.only else None
    asyncio.run(send_actions(args.ws_url, args.target, args.side, only_list, args.delay))


if __name__ == "__main__":
    main()
