import json
import time

from .base import MasterModule


class VoiceModule(MasterModule):
    name = "voice"

    def capabilities(self) -> dict:
        return {
            "tts": {
                "available": True,
                "service": self.context.tts_service,
                "sim_mode": self.context.sim_mode,
            },
            "voice": {
                "tts": {
                    "available": True,
                    "service": self.context.tts_service,
                }
            },
        }

    def status(self) -> dict:
        return {
            "tts_available": True,
            "sim_mode": self.context.sim_mode,
        }

    async def execute_tts(self, text: str) -> dict:
        ok = False
        detail = "tts failed"
        try:
            ok = bool(self.context.send_tts(text))
            detail = "tts ok" if ok else "tts failed"
        except Exception as exc:
            detail = f"tts error: {exc}"
        return {
            "ok": ok,
            "detail": detail,
            "module": self.name,
            "action": "voice.tts",
            "text": text,
        }

    async def handle(self, ws, data: dict) -> bool:
        if data.get("type") != "exec":
            return False

        payload = data.get("payload", {})
        action = payload.get("action") or data.get("action")
        if action != "tts":
            return False

        text = payload.get("text") or data.get("text") or "你好，我是灵犀。"
        result = await self.execute_tts(text)
        reply = {
            "type": "result",
            "robot_id": self.context.robot_id,
            "ts": time.time(),
            "request_id": data.get("request_id") or payload.get("request_id"),
            "source_robot_id": data.get("source_robot_id") or data.get("robot_id"),
            "source_role": data.get("source_role"),
            "target_robot": data.get("target_robot"),
            **result,
        }
        try:
            await ws.send(json.dumps(reply))
        except Exception:
            pass
        return True
