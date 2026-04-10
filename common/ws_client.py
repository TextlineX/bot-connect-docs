# 通用 WebSocket 客户端封装，供主/从调用
import asyncio
import json
import time
from typing import Callable, Optional

import websockets
from websockets.exceptions import ConnectionClosed


class WsClient:
    def __init__(
        self,
        robot_id: str,
        url: str,
        token: Optional[str] = None,
        on_cmd: Optional[Callable[[dict], None]] = None,
        on_exec: Optional[Callable[[dict], None]] = None,
        status_provider: Optional[Callable[[], dict]] = None,
        status_period: float = 2.0,
        on_open: Optional[Callable] = None,
        role: Optional[str] = None,
        config_provider: Optional[Callable[[], dict]] = None,
        on_config_sync: Optional[Callable[[dict], None]] = None,
        verbose: bool = True,
    ):
        self.robot_id = robot_id
        self.url = url
        self.token = token
        self.on_cmd = on_cmd
        self.on_exec = on_exec
        self.status_provider = status_provider or (lambda: {})
        self.status_period = status_period
        self.on_open = on_open
        self.role = role or self._guess_role(robot_id)
        self.config_provider = config_provider or (lambda: {})
        self.on_config_sync = on_config_sync
        self.verbose = verbose

    def _guess_role(self, robot_id: str) -> str:
        rid = str(robot_id or "").strip().lower()
        if rid.startswith("master"):
            return "master"
        if rid.startswith("slave"):
            return "slave"
        if rid.startswith("controller"):
            return "controller"
        return "robot"

    def _runtime_meta(self) -> dict:
        try:
            meta = self.config_provider() or {}
        except Exception:
            meta = {}
        version = meta.get("config_version", meta.get("version", 0))
        try:
            version = int(version or 0)
        except Exception:
            version = 0
        return {
            "role": self.role,
            "config_version": version,
        }

    def _copy_request_meta(self, data: dict) -> dict:
        payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        meta = {}
        for key in (
            "request_id",
            "session",
            "seq",
            "source_robot_id",
            "source_role",
            "target_robot",
            "target_role",
            "config_version",
        ):
            if data.get(key) not in (None, ""):
                meta[key] = data.get(key)
            elif payload.get(key) not in (None, ""):
                meta[key] = payload.get(key)
        return meta

    async def _send_result(self, ws, data: dict, result: dict):
        reply = {
            "type": "result",
            "robot_id": self.robot_id,
            "ts": time.time(),
            **self._runtime_meta(),
            **self._copy_request_meta(data),
            **result,
        }
        try:
            await ws.send(json.dumps(reply, ensure_ascii=False))
        except Exception:
            pass

    async def send_loop(self, ws):
        while True:
            msg = {
                "type": "status",
                "robot_id": self.robot_id,
                "ts": time.time(),
                **self._runtime_meta(),
                "payload": self.status_provider(),
            }
            try:
                await ws.send(json.dumps(msg, ensure_ascii=False))
            except ConnectionClosed:
                break
            await asyncio.sleep(self.status_period)

    async def handle_message(self, ws, data: dict):
        msg_type = data.get("type")
        if msg_type == "config_sync" and self.on_config_sync:
            try:
                res = self.on_config_sync(data)
                if asyncio.iscoroutine(res):
                    res = await res
            except Exception as exc:
                print("config sync error", exc)
                res = None
            try:
                version = data.get("config_version")
                if version in (None, "") and isinstance(data.get("payload"), dict):
                    version = data["payload"].get("version")
                ack = {
                    "type": "config_sync_ack",
                    "robot_id": self.robot_id,
                    "ts": time.time(),
                    **self._runtime_meta(),
                }
                if version not in (None, ""):
                    ack["config_version"] = int(version)
                if isinstance(res, dict) and res:
                    ack["payload"] = res
                await ws.send(json.dumps(ack, ensure_ascii=False))
            except Exception:
                pass
            return

        if msg_type == "cmd_vel" and self.on_cmd:
            if self.verbose:
                payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
                print(f"[ws:{self.robot_id}] cmd_vel from {data.get('robot_id')} -> {payload}")
            res = self.on_cmd(data)
            if asyncio.iscoroutine(res):
                res = await res
            if isinstance(res, dict):
                await self._send_result(ws, data, res)
            return

        if msg_type == "exec" and self.on_exec:
            if self.verbose:
                payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
                action = payload.get("action") or data.get("action")
                print(f"[ws:{self.robot_id}] exec {action} from {data.get('robot_id')} -> {payload}")
            res = self.on_exec(data)
            if asyncio.iscoroutine(res):
                res = await res
            if isinstance(res, dict):
                await self._send_result(ws, data, res)
            return

        if msg_type == "ping":
            await ws.send(
                json.dumps(
                    {
                        "type": "pong",
                        "robot_id": self.robot_id,
                        "ts": time.time(),
                        **self._runtime_meta(),
                    },
                    ensure_ascii=False,
                )
            )

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20) as ws:
                    hello = {
                        "type": "hello",
                        "robot_id": self.robot_id,
                        "ts": time.time(),
                        **self._runtime_meta(),
                    }
                    if self.token:
                        hello["token"] = self.token
                    await ws.send(json.dumps(hello, ensure_ascii=False))

                    tasks = [asyncio.create_task(self.send_loop(ws))]
                    if self.on_open:
                        tasks.append(asyncio.create_task(self.on_open(ws)))

                    async for raw in ws:
                        try:
                            data = json.loads(raw)
                            await self.handle_message(ws, data)
                        except Exception as exc:
                            print("handle error", exc)

                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as exc:
                print("ws reconnect in 3s", exc)
                await asyncio.sleep(3)
