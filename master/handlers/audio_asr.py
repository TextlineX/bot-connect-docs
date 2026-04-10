import json
import time

from .base import MasterModule


class AudioAsrModule(MasterModule):
    name = "audio_asr"

    def capabilities(self) -> dict:
        return {
            "topics": {
                "audio_capture": self.context.audio_topic,
            },
            "asr": {
                "available": bool(self.context.handle_audio_upload),
                "source": "master/audio_upload",
            },
            "audio": {
                "upload_asr": {
                    "available": bool(self.context.handle_audio_upload),
                    "topic": self.context.audio_topic,
                }
            },
        }

    def status(self) -> dict:
        return {"upload_asr_available": bool(self.context.handle_audio_upload)}

    async def handle(self, ws, data: dict) -> bool:
        if data.get("type") != "audio_upload" or not self.context.handle_audio_upload:
            return False

        text = await self.context.handle_audio_upload(data)
        payload = data.get("payload", {})
        reply = {
            "type": "asr_text",
            "robot_id": self.context.robot_id,
            "ts": time.time(),
            "text": text or "",
            "detail": "from master/audio_upload",
            "session": payload.get("session"),
            "seq": payload.get("seq"),
            "final": payload.get("final", False),
            "module": self.name,
        }
        try:
            await ws.send(json.dumps(reply))
        except Exception:
            pass
        return True
