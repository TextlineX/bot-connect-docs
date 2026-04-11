#!/usr/bin/env python3
# 从机示例：支持 config_sync 持久化，cmd_vel / TTS 执行并回传 result
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
if COMMON.as_posix() not in sys.path:
    sys.path.insert(0, COMMON.as_posix())

from ws_client import WsClient
from role_config import save_role_config
from runtime import build_runtime
from action_presets import canonical_action, resolve_preset

ROLE_STATE, config_provider, on_config_sync = build_runtime(
    "slave",
    {
        "robot_id": "slave-01",
        "config_version": 0,
        "routing": {
            "brain_robot_id": "master-01",
            "control_robot_id": "slave-01",
        },
    },
)

WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")
ROBOT_ID = os.getenv("ROBOT_ID", str(ROLE_STATE.get("robot_id") or "slave-01"))
ROLE_STATE["robot_id"] = ROBOT_ID
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
SIM_MODE = os.getenv("SIM_MODE", "1") == "1"
START_TS = time.time()

try:
    import rclpy  # type: ignore
    from geometry_msgs.msg import Twist  # type: ignore

    RCLPY_READY = True
except Exception:
    RCLPY_READY = False

try:
    from tts_client import send_tts as ros_send_tts  # type: ignore
except Exception:
    ros_send_tts = None

try:
    from preset_motion_client import run_preset as ros_run_preset  # type: ignore
except Exception:
    ros_run_preset = None


class RobotSDK:
    def __init__(self):
        self.last_velocity = {"linear": 0.0, "angular": 0.0, "at": None}
        self.node = None
        self.cmd_pub = None
        if RCLPY_READY and not SIM_MODE:
            try:
                rclpy.init(args=None)
                from rclpy.node import Node  # type: ignore

                class _Node(Node):
                    pass

                self.node = _Node("slave_cmd_bridge")
                self.cmd_pub = self.node.create_publisher(Twist, "/cmd_vel", 10)
                print("[SLAVE SDK] ROS cmd_vel publisher ready")
            except Exception as exc:
                print(f"[SLAVE SDK] ROS init failed: {exc}")
                self.node = None
                self.cmd_pub = None

    def set_velocity(self, linear: float, angular: float):
        self.last_velocity = {"linear": float(linear), "angular": float(angular), "at": time.time()}
        if self.cmd_pub:
            try:
                msg = Twist()
                msg.linear.x = float(linear)
                msg.angular.z = float(angular)
                self.cmd_pub.publish(msg)
                print(f"[SLAVE SDK] publish cmd_vel linear={linear} angular={angular}")
            except Exception as exc:
                print(f"[SLAVE SDK] publish cmd_vel failed: {exc}")
        else:
            print(f"[SLAVE SDK] set_velocity (sim) linear={linear} angular={angular}")

    def status(self):
        now = time.time()
        elapsed = now - START_TS
        last_move_at = self.last_velocity.get("at")
        battery_ratio = round(0.8 - min(elapsed / 36000, 0.15), 2)
        return {
            "ts": now,
            "battery": battery_ratio,
            "system": {
                "hostname": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "slave-local",
                "ws_url": WS_URL,
                "sim_mode": SIM_MODE,
                "local_test": True,
                "runtime_label": "本地模拟从机",
                "uptime_sec": round(elapsed, 1),
            },
            "motion": {
                "linear": self.last_velocity.get("linear", 0.0),
                "angular": self.last_velocity.get("angular", 0.0),
                "last_command_age_sec": round(now - last_move_at, 1) if last_move_at else None,
            },
            "audio": {
                "tts_ready": bool(ros_send_tts),
                "asr_bridge_ready": False,
            },
            "sensors": {
                "battery_pct": int(battery_ratio * 100),
                "network_pct": 96,
                "audio_level_pct": int(24 + 10 * math.sin(elapsed / 4.2)),
                "imu_yaw_deg": round((elapsed * 9) % 360, 1),
                "lidar_distance_m": round(1.8 + 0.35 * math.sin(elapsed / 5.0), 2),
                "motor_temp_c": round(34 + 2.5 * math.sin(elapsed / 8.0), 1),
                "posture": "tracking",
            },
        }


sdk = RobotSDK()


def on_cmd(data):
    payload = data.get("payload", {})
    sdk.set_velocity(payload.get("linear", 0), payload.get("angular", 0))
    return {
        "ok": True,
        "detail": "cmd_vel handled",
        "module": "slave",
        "action": "cmd_vel",
        "payload": payload,
    }


def _do_tts(text: str) -> dict:
    if ros_send_tts:
        try:
            ok = bool(ros_send_tts(text))
            return {"ok": ok, "detail": "tts ok" if ok else "tts failed"}
        except Exception as exc:
            return {"ok": False, "detail": f"tts error: {exc}"}
    return {"ok": False, "detail": "tts unavailable (no rclpy/tts_client)"}


def _do_preset(name: str, motion_id=None, area_id=None, interrupt=False) -> dict:
    if ros_run_preset:
        try:
            ok = bool(ros_run_preset(name, motion_id=motion_id, area_id=area_id, interrupt=interrupt))
            return {"ok": ok, "detail": "preset ok" if ok else "preset failed"}
        except Exception as exc:
            return {"ok": False, "detail": f"preset error: {exc}"}
    return {"ok": False, "detail": "preset unavailable (no rclpy/preset_motion_client)"}


def on_exec(data):
    payload = data.get("payload", {})
    raw_action = payload.get("action") or data.get("action")
    raw_action = str(raw_action or "").strip()
    action = canonical_action(raw_action)
    if action == "voice.tts":
        text = payload.get("text") or payload.get("message") or "你好，我是从机。"
        result = _do_tts(str(text))
        result.update({"module": "slave", "action": "voice.tts", "text": text})
        return result

    if action == "motion.move":
        sdk.set_velocity(payload.get("linear", 0), payload.get("angular", 0))
        return {
            "ok": True,
            "detail": "motion move ok",
            "module": "slave",
            "action": "motion.move",
            "payload": payload,
        }

    if action == "motion.stop":
        sdk.set_velocity(0, 0)
        return {
            "ok": True,
            "detail": "motion stop ok",
            "module": "slave",
            "action": "motion.stop",
            "payload": {"linear": 0, "angular": 0},
        }

    if action == "preset.run":
        preset = resolve_preset(raw_action, payload)
        if not preset:
            print(f"[SLAVE EXEC] unsupported preset raw={raw_action} payload={payload}")
            return {
                "ok": False,
                "detail": f"unsupported preset: {raw_action}",
                "module": "slave",
                "action": "preset.run",
                "payload": payload,
            }
        res = _do_preset(
            str(preset["name"]),
            motion_id=preset["motion_id"],
            area_id=preset["area_id"],
            interrupt=preset["interrupt"],
        )
        res.update({
            "module": "slave",
            "action": "preset.run",
            "detail": f"{res.get('detail')} | {preset['label']}",
            "payload": {
                "name": preset["name"],
                "motion_id": preset["motion_id"],
                "area_id": preset["area_id"],
                "interrupt": preset["interrupt"],
                "label": preset["label"],
                "raw_action": raw_action,
            },
        })
        print(
            "[SLAVE EXEC] preset",
            f"raw={raw_action}",
            f"name={preset['name']}",
            f"motion_id={preset['motion_id']}",
            f"area_id={preset['area_id']}",
            f"interrupt={preset['interrupt']}",
            f"ok={res.get('ok')}",
        )
        return res

    print("[SLAVE EXEC] unsupported", data)
    return {
        "ok": False,
        "detail": f"unsupported action: {action}",
        "module": "slave",
        "action": action,
        "payload": payload,
    }


def status_provider():
    return {
        "role": "slave",
        "config_version": int(ROLE_STATE.get("config_version") or 0),
        **sdk.status()
    }


def main():
    save_role_config("slave", ROLE_STATE)
    client = WsClient(
        ROBOT_ID,
        WS_URL,
        AUTH_TOKEN,
        on_cmd=on_cmd,
        on_exec=on_exec,
        status_provider=status_provider,
        role="slave",
        config_provider=config_provider,
        on_config_sync=on_config_sync,
        verbose=True,
    )
    import asyncio

    asyncio.run(client.run())


if __name__ == "__main__":
    main()
