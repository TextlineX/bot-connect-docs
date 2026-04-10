import asyncio
import json
import time

from .base import MasterModule

PRESET_DEFS = {
    "wave": {"name": "wave", "motion_id": 1002, "area_id": 2, "label": "右手挥手"},
    "wave_left": {"name": "wave_left", "motion_id": 1002, "area_id": 1, "label": "左手挥手"},
    "handshake": {"name": "handshake", "motion_id": 1003, "area_id": 2, "label": "右手握手"},
    "handshake_left": {
        "name": "handshake_left",
        "motion_id": 1003,
        "area_id": 1,
        "label": "左手握手",
    },
    "raise_hand": {"name": "raise_hand", "motion_id": 1001, "area_id": 2, "label": "右手举手"},
    "raise_hand_left": {
        "name": "raise_hand_left",
        "motion_id": 1001,
        "area_id": 1,
        "label": "左手举手",
    },
    "kiss": {"name": "kiss", "motion_id": 1004, "area_id": 2, "label": "右手飞吻"},
    "kiss_left": {"name": "kiss_left", "motion_id": 1004, "area_id": 1, "label": "左手飞吻"},
    "salute": {"name": "salute", "motion_id": 1013, "area_id": 2, "label": "右手敬礼"},
    "salute_left": {"name": "salute_left", "motion_id": 1013, "area_id": 1, "label": "左手敬礼"},
    "clap": {"name": "clap", "motion_id": 3017, "area_id": 11, "label": "鼓掌"},
    "cheer": {"name": "cheer", "motion_id": 3011, "area_id": 11, "label": "加油"},
    "bow": {"name": "bow", "motion_id": 3001, "area_id": 11, "label": "鞠躬"},
    "dance": {"name": "dance", "motion_id": 3007, "area_id": 11, "label": "动感光波"},
}

ACTION_ALIASES = {
    "tts": "voice.tts",
    "say": "voice.tts",
    "speak": "voice.tts",
    "说话": "voice.tts",
    "播报": "voice.tts",
    "move": "motion.move",
    "move_forward": "motion.move",
    "move_backward": "motion.move",
    "turn_left": "motion.move",
    "turn_right": "motion.move",
    "前进": "motion.move",
    "后退": "motion.move",
    "左转": "motion.move",
    "右转": "motion.move",
    "stop": "motion.stop",
    "halt": "motion.stop",
    "停止": "motion.stop",
    "刹车": "motion.stop",
    "wave": "preset.run",
    "handshake": "preset.run",
    "raise_hand": "preset.run",
    "kiss": "preset.run",
    "salute": "preset.run",
    "clap": "preset.run",
    "cheer": "preset.run",
    "bow": "preset.run",
    "dance": "preset.run",
    "挥手": "preset.run",
    "握手": "preset.run",
    "举手": "preset.run",
    "飞吻": "preset.run",
    "敬礼": "preset.run",
    "鼓掌": "preset.run",
    "加油": "preset.run",
    "鞠躬": "preset.run",
    "跳舞": "preset.run",
}

PRESET_ALIASES = {
    "wave": "wave",
    "挥手": "wave",
    "右手挥手": "wave",
    "wave_left": "wave_left",
    "left_wave": "wave_left",
    "左手挥手": "wave_left",
    "handshake": "handshake",
    "握手": "handshake",
    "右手握手": "handshake",
    "handshake_left": "handshake_left",
    "left_handshake": "handshake_left",
    "左手握手": "handshake_left",
    "raise_hand": "raise_hand",
    "举手": "raise_hand",
    "右手举手": "raise_hand",
    "raise_hand_left": "raise_hand_left",
    "left_raise_hand": "raise_hand_left",
    "左手举手": "raise_hand_left",
    "kiss": "kiss",
    "飞吻": "kiss",
    "右手飞吻": "kiss",
    "kiss_left": "kiss_left",
    "left_kiss": "kiss_left",
    "左手飞吻": "kiss_left",
    "salute": "salute",
    "敬礼": "salute",
    "右手敬礼": "salute",
    "salute_left": "salute_left",
    "left_salute": "salute_left",
    "左手敬礼": "salute_left",
    "clap": "clap",
    "鼓掌": "clap",
    "cheer": "cheer",
    "加油": "cheer",
    "bow": "bow",
    "鞠躬": "bow",
    "dance": "dance",
    "跳舞": "dance",
}


class ActionRouterModule(MasterModule):
    name = "action_router"

    def __init__(self, context):
        super().__init__(context)
        self._stop_task = None

    def capabilities(self) -> dict:
        return {
            "actions": {
                "available": True,
                "supported": [
                    "voice.tts",
                    "motion.move",
                    "motion.stop",
                    "preset.run",
                ],
                "aliases": ACTION_ALIASES,
                "presets": list(PRESET_DEFS.keys()),
            }
        }

    def status(self) -> dict:
        return {"action_router_available": True}

    async def handle(self, ws, data: dict) -> bool:
        if data.get("type") != "exec":
            return False

        payload = data.get("payload", {})
        action = payload.get("action") or data.get("action")
        if not action or action == "tts":
            return False

        result = await self.execute_action(action, payload)
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
            await ws.send(json.dumps(reply, ensure_ascii=False))
        except Exception:
            pass
        return result.get("handled", False)

    async def execute_action(self, action: str, payload: dict | None = None) -> dict:
        payload = payload or {}
        canonical = self._canonical_action(action)
        if canonical == "voice.tts":
            if not self.context.voice_module:
                return self._result(False, canonical, "voice module unavailable", handled=True)
            text = str(payload.get("text") or payload.get("message") or "").strip()
            if not text:
                return self._result(False, canonical, "missing text", handled=True)
            return self._result_from(await self.context.voice_module.execute_tts(text), handled=True)

        if canonical == "motion.stop":
            if not self.context.motion_module:
                return self._result(False, canonical, "motion module unavailable", handled=True)
            if self._stop_task:
                self._stop_task.cancel()
                self._stop_task = None
            return self._result_from(await self.context.motion_module.execute_stop(), handled=True)

        if canonical == "motion.move":
            if not self.context.motion_module:
                return self._result(False, canonical, "motion module unavailable", handled=True)
            linear, angular = self._resolve_motion_payload(action, payload)
            duration = self._to_float(payload.get("duration"), 0)
            result = await self.context.motion_module.execute_move(linear, angular)
            if duration > 0:
                if self._stop_task:
                    self._stop_task.cancel()
                self._stop_task = asyncio.create_task(self._stop_after(duration))
                result["payload"]["duration"] = duration
                result["detail"] = f"{result['detail']} duration={duration}"
            return self._result_from(result, handled=True)

        if canonical == "preset.run":
            preset = self._resolve_preset_payload(action, payload)
            if not preset:
                return self._result(False, canonical, f"unsupported preset: {action}", handled=True)
            ok = bool(
                self.context.sdk.run_preset(
                    preset["name"],
                    motion_id=preset["motion_id"],
                    area_id=preset["area_id"],
                    interrupt=preset["interrupt"],
                )
            )
            detail = "preset ok" if ok else "preset failed"
            return self._result(
                ok,
                canonical,
                f"{detail}: {preset['label']}",
                handled=True,
                payload={
                    "name": preset["name"],
                    "motion_id": preset["motion_id"],
                    "area_id": preset["area_id"],
                    "interrupt": preset["interrupt"],
                    "label": preset["label"],
                },
            )

        return self._result(False, canonical, f"unsupported action: {action}", handled=False)

    async def _stop_after(self, duration: float):
        try:
            await asyncio.sleep(duration)
            await self.context.motion_module.execute_stop()
        except asyncio.CancelledError:
            return

    def _canonical_action(self, action: str) -> str:
        value = str(action or "").strip()
        return ACTION_ALIASES.get(value, value)

    def _resolve_motion_payload(self, action: str, payload: dict):
        linear = self._to_float(payload.get("linear"), 0)
        angular = self._to_float(payload.get("angular"), 0)
        alias = str(action or "").strip()
        if alias == "motion.move":
            alias = str(payload.get("keyword") or payload.get("intent") or alias).strip()
        if alias == "move_forward" and not linear:
            linear = self._to_float(payload.get("speed"), 0.2)
        elif alias == "move_backward" and not linear:
            linear = -abs(self._to_float(payload.get("speed"), 0.2))
        elif alias == "turn_left" and not angular:
            angular = abs(self._to_float(payload.get("speed"), 0.3))
        elif alias == "turn_right" and not angular:
            angular = -abs(self._to_float(payload.get("speed"), 0.3))
        elif alias == "前进" and not linear:
            linear = self._to_float(payload.get("speed"), 0.2)
        elif alias == "后退" and not linear:
            linear = -abs(self._to_float(payload.get("speed"), 0.2))
        elif alias == "左转" and not angular:
            angular = abs(self._to_float(payload.get("speed"), 0.3))
        elif alias == "右转" and not angular:
            angular = -abs(self._to_float(payload.get("speed"), 0.3))
        return linear, angular

    def _resolve_preset_payload(self, action: str, payload: dict) -> dict | None:
        motion_id = self._to_int(payload.get("motion_id"))
        area_id = self._to_int(payload.get("area_id"))
        interrupt = self._to_bool(payload.get("interrupt"), False)
        name = str(
            payload.get("name")
            or payload.get("preset")
            or payload.get("action_name")
            or payload.get("keyword")
            or action
        ).strip()
        if motion_id is not None and area_id is not None:
            return {
                "name": name or "custom",
                "motion_id": motion_id,
                "area_id": area_id,
                "interrupt": interrupt,
                "label": name or "custom",
            }
        preset_name = PRESET_ALIASES.get(name)
        if not preset_name:
            return None
        preset = PRESET_DEFS[preset_name]
        return {**preset, "interrupt": interrupt}

    def _to_float(self, value, default: float) -> float:
        try:
            if value in ("", None):
                return default
            return float(value)
        except Exception:
            return default

    def _to_int(self, value):
        try:
            if value in ("", None):
                return None
            return int(value)
        except Exception:
            return None

    def _to_bool(self, value, default: bool) -> bool:
        if value in ("", None):
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def _result(self, ok: bool, action: str, detail: str, handled: bool, payload: dict | None = None):
        return {
            "ok": ok,
            "detail": detail,
            "module": self.name,
            "action": action,
            "handled": handled,
            "payload": payload or {},
        }

    def _result_from(self, result: dict, handled: bool):
        merged = dict(result)
        merged["handled"] = handled
        return merged
