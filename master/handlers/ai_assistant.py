import asyncio
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .base import MasterModule

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT / "config" / "master_config.json"


def deep_merge(base: dict, extra: dict) -> dict:
    merged = dict(base)
    for key, value in (extra or {}).items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def default_config() -> dict:
    return {
        "config_version": 0,
        "ai": {
            "enabled": False,
            "auto_tts": True,
            "allow_action_execution": False,
            "forward_action_to_slave": False,
            "forward_action_target": "slave-01",
            "behavior_lock_enabled": True,
            "behavior_lock_timeout_sec": 20,
            "trigger_on_partial": False,
            "listen_robot_ids": [],
            "ignore_robot_ids": [],
            "tts_target_robot": "slave-01",
            "provider": "anthropic_compatible",
            "api_base": "https://api.minimaxi.com/anthropic",
            "chat_endpoint": "https://api.minimaxi.com/anthropic/v1/messages",
            "api_key": "",
            "api_key_header": "x-api-key",
            "api_key_prefix": "",
            "model": "MiniMax-M2.7",
            "temperature": 0.2,
            "timeout_sec": 20,
            "json_mode": True,
            "max_tokens": 1024,
            "anthropic_version": "2023-06-01",
            "extra_headers": {},
            "extra_body": {},
            "retry_attempts": 3,
            "retry_backoff_sec": 0.5,
            "system_prompt": (
                "你是机器人主机的语音指令解析助手。"
                "必须返回一个 JSON 对象。"
                "JSON 中必须包含字符串字段 message，用于 TTS 播报。"
                "可以包含 intent、action、params、keywords、confidence、reason 等任意自定义字段。"
                "不要输出 JSON 之外的任何文本。"
            ),
        }
    }


def load_config(path: Path) -> dict:
    cfg = default_config()
    if not path.exists():
        return cfg
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return deep_merge(cfg, raw)
    except Exception as exc:
        print(f"[master.ai] config load failed: {exc}")
    return cfg


def parse_json_text(text: str):
    raw = str(text or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        return json.loads(raw)
    except Exception:
        return None


class AiAssistantModule(MasterModule):
    name = "ai_assistant"

    def __init__(self, context):
        super().__init__(context)
        env_path = os.getenv("MASTER_CONFIG_PATH", "")
        self.config_path = Path(env_path) if env_path else DEFAULT_CONFIG_PATH
        self.config = load_config(self.config_path)
        self.runtime_ai = {}
        self._seen = []
        self._active_action_lock = None

    def _ai_cfg(self) -> dict:
        return deep_merge(self.config.get("ai", {}), self.runtime_ai)

    def _current_config_version(self) -> int:
        try:
            return int(self.config.get("config_version") or 0)
        except Exception:
            return 0

    def _persist_ai_config(self):
        payload = {
            "config_version": self._current_config_version(),
            "ai": self._ai_cfg(),
        }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.config = load_config(self.config_path)

    def _active_lock(self):
        lock = self._active_action_lock
        if not lock:
            return None
        if lock.get("expires_at", 0) <= time.time():
            self._active_action_lock = None
            return None
        return lock

    def _set_lock(self, request_id: str, action: str, target_robot: str, input_text: str, timeout_sec: float):
        self._active_action_lock = {
            "request_id": request_id,
            "action": action,
            "target_robot": target_robot,
            "input_text": input_text,
            "expires_at": time.time() + max(1.0, float(timeout_sec or 20)),
        }

    def _clear_lock(self):
        self._active_action_lock = None

    def capabilities(self) -> dict:
        cfg = self._ai_cfg()
        return {
            "ai": {
                "available": True,
                "enabled": bool(cfg.get("enabled")),
                "auto_tts": bool(cfg.get("auto_tts", True)),
                "allow_action_execution": bool(cfg.get("allow_action_execution", False)),
                "behavior_lock_enabled": bool(cfg.get("behavior_lock_enabled", True)),
                "busy": bool(self._active_lock()),
                "config_path": str(self.config_path),
            }
        }

    def status(self) -> dict:
        cfg = self._ai_cfg()
        return {
            "enabled": bool(cfg.get("enabled")),
            "auto_tts": bool(cfg.get("auto_tts", True)),
            "allow_action_execution": bool(cfg.get("allow_action_execution", False)),
            "behavior_lock_enabled": bool(cfg.get("behavior_lock_enabled", True)),
            "busy": bool(self._active_lock()),
            "config_path": str(self.config_path),
        }

    async def _emit_ai_event(
        self,
        ws,
        *,
        source_robot_id: str,
        source_session,
        source_seq,
        input_text: str,
        stage: str,
        ok=None,
        detail: str = "",
        data_obj=None,
        action_result=None,
        triggered=None,
        called=None,
        skip_reason: str = "",
    ):
        payload = {
            "type": "ai_result",
            "robot_id": self.context.robot_id,
            "ts": time.time(),
            "module": self.name,
            "source_robot_id": source_robot_id,
            "source_session": source_session,
            "source_seq": source_seq,
            "input_text": input_text,
            "stage": stage,
            "ok": ok,
            "detail": detail,
            "data": data_obj,
            "action_result": action_result,
            "triggered": triggered,
            "called": called,
            "skip_reason": skip_reason,
        }
        try:
            await ws.send(json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass

    async def handle(self, ws, data: dict) -> bool:
        msg_type = data.get("type")
        if msg_type == "master_config_update":
            await self._handle_runtime_update(ws, data)
            return True
        if msg_type == "config_sync":
            await self._handle_config_sync(ws, data)
            return True
        if msg_type == "result":
            return await self._handle_result(data)
        if msg_type == "asr_text":
            return await self._handle_asr_text(ws, data)
        return False

    async def _handle_runtime_update(self, ws, data: dict):
        payload = data.get("payload", {})
        ai_payload = payload.get("ai", payload if isinstance(payload, dict) else {})
        if isinstance(ai_payload, dict):
            self.runtime_ai = deep_merge(self.runtime_ai, ai_payload)
        version = data.get("config_version")
        if version not in (None, ""):
            self.config["config_version"] = int(version)
        self._persist_ai_config()
        ack = {
            "type": "master_config_ack",
            "robot_id": self.context.robot_id,
            "ts": time.time(),
            "module": self.name,
            "payload": {
                "ai": self._ai_cfg(),
            },
        }
        try:
            await ws.send(json.dumps(ack))
        except Exception:
            pass

    async def _handle_config_sync(self, ws, data: dict):
        payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        role_cfg = payload.get("role_config") if isinstance(payload.get("role_config"), dict) else {}
        master_cfg = payload.get("config", {}).get("master") if isinstance(payload.get("config"), dict) else {}
        next_cfg = {}
        if isinstance(master_cfg, dict):
            next_cfg = deep_merge(next_cfg, master_cfg)
        if isinstance(role_cfg, dict):
            next_cfg = deep_merge(next_cfg, role_cfg)
        if isinstance(next_cfg.get("ai"), dict):
            self.runtime_ai = deep_merge({}, next_cfg.get("ai"))
        version = payload.get("version", data.get("config_version"))
        if version not in (None, ""):
            self.config["config_version"] = int(version)
        if isinstance(next_cfg.get("ai"), dict):
            self.config = deep_merge(self.config, {
                "config_version": self._current_config_version(),
                "ai": next_cfg.get("ai"),
            })
            self._persist_ai_config()

    async def _handle_result(self, data: dict) -> bool:
        lock = self._active_lock()
        if not lock:
            return False
        if str(data.get("request_id") or "").strip() != str(lock.get("request_id") or "").strip():
            return False
        self._clear_lock()
        return False

    async def _handle_asr_text(self, ws, data: dict) -> bool:
        cfg = self._ai_cfg()
        text = (data.get("text") or "").strip()
        source_robot = data.get("robot_id") or ""
        source_session = data.get("session")
        source_seq = data.get("seq")

        async def skip(reason: str, detail: str):
            await self._emit_ai_event(
                ws,
                source_robot_id=source_robot,
                source_session=source_session,
                source_seq=source_seq,
                input_text=text,
                stage="skipped",
                ok=None,
                detail=detail,
                triggered=False,
                called=False,
                skip_reason=reason,
            )
            return False

        if not cfg.get("enabled"):
            if text:
                return await skip("ai_disabled", "ai disabled")
            return False

        if not text:
            return False

        if source_robot == self.context.robot_id:
            return await skip("self_message", "skip self asr_text")

        listen = cfg.get("listen_robot_ids") or []
        ignore = cfg.get("ignore_robot_ids") or []
        if listen and source_robot not in listen:
            return await skip("not_in_listen_robot_ids", "source robot not in listen list")
        if ignore and source_robot in ignore:
            return await skip("in_ignore_robot_ids", "source robot ignored")

        is_final = data.get("final")
        if is_final is False and not cfg.get("trigger_on_partial", False):
            return await skip("partial_disabled", "partial asr disabled")

        lock = self._active_lock()
        if cfg.get("behavior_lock_enabled", True) and lock:
            return await skip(
                "behavior_locked",
                f"waiting action={lock.get('action')} target={lock.get('target_robot')}",
            )

        dedupe_key = (
            source_robot,
            source_session,
            source_seq,
            text,
            bool(is_final),
        )
        if dedupe_key in self._seen:
            return await skip("duplicate", "duplicate asr_text")
        self._seen.append(dedupe_key)
        if len(self._seen) > 100:
            self._seen.pop(0)

        await self._emit_ai_event(
            ws,
            source_robot_id=source_robot,
            source_session=source_session,
            source_seq=source_seq,
            input_text=text,
            stage="calling",
            ok=None,
            detail="ai request started",
            triggered=True,
            called=True,
        )

        result = await asyncio.to_thread(self._call_ai, text, data, cfg)
        action_result = None
        did_tts_via_action = False
        data_obj = result.get("data")
        if result.get("ok") and isinstance(data_obj, dict):
            action_name = str(data_obj.get("action") or data_obj.get("keyword") or "").strip()
            if action_name:
                action_payload = data_obj.get("params") if isinstance(data_obj.get("params"), dict) else {}
                action_payload = dict(action_payload)
                for key in ("message", "keyword", "intent"):
                    value = data_obj.get(key)
                    if value not in ("", None) and key not in action_payload:
                        action_payload[key] = value
                allow_action_execution = bool(cfg.get("allow_action_execution", False))
                forward = bool(cfg.get("forward_action_to_slave"))
                forward_target = str(cfg.get("forward_action_target") or "slave-01").strip() or "slave-01"
                if not allow_action_execution:
                    self._clear_lock()
                    action_result = {
                        "ok": False,
                        "detail": "ai action blocked: execution disabled",
                        "module": self.name,
                        "action": action_name,
                        "handled": False,
                        "payload": action_payload,
                    }
                elif forward:
                    request_id = (
                        f"ai-{int(time.time() * 1000)}-"
                        f"{source_robot or 'unknown'}-{source_seq or '0'}"
                    )
                    forward_msg = {
                        "type": "exec",
                        "robot_id": self.context.robot_id,
                        "target_robot": forward_target,
                        "request_id": request_id,
                        "source_robot_id": self.context.robot_id,
                        "source_role": "master",
                        "payload": {
                            "action": action_name,
                            "request_id": request_id,
                            "source_robot_id": self.context.robot_id,
                            "source_role": "master",
                            **action_payload,
                        },
                        "ts": time.time(),
                    }
                    try:
                        await ws.send(json.dumps(forward_msg, ensure_ascii=False))
                        if cfg.get("behavior_lock_enabled", True):
                            self._set_lock(
                                request_id,
                                action_name,
                                forward_target,
                                text,
                                float(cfg.get("behavior_lock_timeout_sec") or 20),
                            )
                        action_result = {
                            "ok": True,
                            "detail": f"forwarded to {forward_target}",
                            "module": self.name,
                            "action": action_name,
                            "handled": True,
                            "payload": action_payload,
                            "forward_target": forward_target,
                            "request_id": request_id,
                        }
                    except Exception as exc:
                        self._clear_lock()
                        action_result = {
                            "ok": False,
                            "detail": f"forward error: {exc}",
                            "module": self.name,
                            "action": action_name,
                            "handled": True,
                            "payload": action_payload,
                            "forward_target": forward_target,
                            "request_id": request_id,
                        }
                elif self.context.execute_action:
                    try:
                        action_result = await self.context.execute_action(action_name, action_payload)
                        self._clear_lock()
                    except Exception as exc:
                        action_result = {
                            "ok": False,
                            "detail": f"action execute error: {exc}",
                            "module": self.name,
                            "action": action_name,
                            "handled": True,
                            "payload": action_payload,
                        }
                else:
                    self._clear_lock()
                    action_result = {
                        "ok": False,
                        "detail": "action router unavailable",
                        "module": self.name,
                        "action": action_name,
                        "handled": True,
                        "payload": action_payload,
                    }
                did_tts_via_action = bool(
                    action_result
                    and action_result.get("ok")
                    and action_result.get("action") == "voice.tts"
                )
        await self._emit_ai_event(
            ws,
            source_robot_id=source_robot,
            source_session=source_session,
            source_seq=source_seq,
            input_text=text,
            stage="completed",
            ok=result.get("ok", False),
            detail=result.get("detail", ""),
            data_obj=data_obj,
            action_result=action_result,
            triggered=True,
            called=True,
        )

        if result.get("ok") and isinstance(data_obj, dict):
            if action_result:
                try:
                    await ws.send(
                        json.dumps(
                            {
                                "type": "result",
                                "robot_id": self.context.robot_id,
                                "ts": time.time(),
                                "source": "ai_assistant",
                                "source_robot_id": source_robot,
                                "input_text": text,
                                **action_result,
                            },
                            ensure_ascii=False,
                        )
                    )
                except Exception:
                    pass
            message = str(data_obj.get("message") or "").strip()
            if message and cfg.get("auto_tts", True) and not did_tts_via_action:
                # 优先用显式目标，其次用动作转发目标，再次回退到 slave-01
                tts_target = str(
                    cfg.get("tts_target_robot")
                    or cfg.get("forward_action_target")
                    or "slave-01"
                ).strip()
                if tts_target and tts_target != self.context.robot_id:
                    request_id = (
                        f"ai-tts-{int(time.time() * 1000)}-"
                        f"{source_robot or 'unknown'}-{source_seq or '0'}"
                    )
                    try:
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "exec",
                                    "robot_id": self.context.robot_id,
                                    "target_robot": tts_target,
                                    "request_id": request_id,
                                    "source_robot_id": self.context.robot_id,
                                    "source_role": "master",
                                    "payload": {
                                        "action": "voice.tts",
                                        "text": message,
                                        "request_id": request_id,
                                        "source_robot_id": self.context.robot_id,
                                        "source_role": "master",
                                    },
                                    "ts": time.time(),
                                },
                                ensure_ascii=False,
                            )
                        )
                        if cfg.get("behavior_lock_enabled", True):
                            self._set_lock(
                                request_id,
                                "voice.tts",
                                tts_target,
                                text,
                                float(cfg.get("behavior_lock_timeout_sec") or 20),
                            )
                        await self._emit_ai_event(
                            ws,
                            source_robot_id=source_robot,
                            source_session=source_session,
                            source_seq=source_seq,
                            input_text=text,
                            stage="completed",
                            ok=True,
                            detail=f"ai tts forwarded to {tts_target}",
                            data_obj=data_obj,
                            action_result=action_result,
                            triggered=True,
                            called=True,
                        )
                    except Exception:
                        self._clear_lock()
                        pass
                else:
                    try:
                        ok = bool(self.context.send_tts(message))
                        self._clear_lock()
                        tts_reply = {
                            "type": "result",
                            "robot_id": self.context.robot_id,
                            "ts": time.time(),
                            "ok": ok,
                            "detail": "ai tts ok" if ok else "ai tts failed",
                            "module": self.name,
                            "action": "ai_tts",
                            "text": message,
                        }
                        await ws.send(json.dumps(tts_reply, ensure_ascii=False))
                    except Exception:
                        pass
        return False

    def _call_ai(self, text: str, source: dict, cfg: dict) -> dict:
        provider = str(cfg.get("provider") or "openai").strip().lower()
        api_key = str(cfg.get("api_key") or "").strip()
        model = str(cfg.get("model") or "").strip()
        api_base = str(cfg.get("api_base") or "").strip().rstrip("/")
        default_endpoint = f"{api_base}/chat/completions"
        if provider in {"anthropic", "anthropic_compatible"}:
            default_endpoint = f"{api_base}/v1/messages"
        endpoint = str(cfg.get("chat_endpoint") or "").strip() or default_endpoint
        timeout_sec = float(cfg.get("timeout_sec") or 20)
        retry_attempts = max(1, int(cfg.get("retry_attempts") or 1))
        retry_backoff = float(cfg.get("retry_backoff_sec") or 0.0)

        if not endpoint:
            return {"ok": False, "detail": "missing ai endpoint", "data": None}
        if not api_key:
            return {"ok": False, "detail": "missing ai api_key", "data": None}
        if not model:
            return {"ok": False, "detail": "missing ai model", "data": None}

        user_payload = {
            "text": text,
            "source_robot_id": source.get("robot_id"),
            "session": source.get("session"),
            "seq": source.get("seq"),
            "final": source.get("final"),
        }
        if provider in {"anthropic", "anthropic_compatible"}:
            body = {
                "model": model,
                "temperature": cfg.get("temperature", 0.2),
                "max_tokens": int(cfg.get("max_tokens") or 1024),
                "system": cfg.get("system_prompt", ""),
                "messages": [
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
            }
        else:
            body = {
                "model": model,
                "temperature": cfg.get("temperature", 0.2),
                "messages": [
                    {"role": "system", "content": cfg.get("system_prompt", "")},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
            }
            if cfg.get("json_mode", True):
                body["response_format"] = {"type": "json_object"}
        extra_body = cfg.get("extra_body") or {}
        if isinstance(extra_body, dict):
            body.update(extra_body)

        headers = {"Content-Type": "application/json"}
        if provider in {"anthropic", "anthropic_compatible"}:
            header_name = str(cfg.get("api_key_header") or "x-api-key")
            prefix = str(cfg.get("api_key_prefix") or "")
            headers[header_name] = f"{prefix}{api_key}"
            headers["anthropic-version"] = str(cfg.get("anthropic_version") or "2023-06-01")
        else:
            prefix = str(cfg.get("api_key_prefix") or "Bearer ")
            header_name = str(cfg.get("api_key_header") or "Authorization")
            headers[header_name] = f"{prefix}{api_key}"
        extra_headers = cfg.get("extra_headers") or {}
        if isinstance(extra_headers, dict):
            headers.update({str(k): str(v) for k, v in extra_headers.items()})

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        last_error = None
        for attempt in range(retry_attempts):
            try:
                with urllib.request.urlopen(request, timeout=timeout_sec) as resp:
                    raw = resp.read().decode("utf-8")
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="ignore")
                last_error = f"http {exc.code}: {detail}"
                if exc.code in (429, 500, 502, 503, 504, 529) and attempt + 1 < retry_attempts:
                    time.sleep(retry_backoff * (attempt + 1))
                    continue
                return {"ok": False, "detail": last_error, "data": None}
            except Exception as exc:
                last_error = f"ai request failed: {exc}"
                if attempt + 1 < retry_attempts:
                    time.sleep(retry_backoff * (attempt + 1))
                    continue
                return {"ok": False, "detail": last_error, "data": None}

        try:
            parsed = json.loads(raw)
        except Exception as exc:
            return {"ok": False, "detail": f"invalid ai response json: {exc}", "data": raw}

        data = self._extract_ai_json(parsed)
        if not isinstance(data, dict):
            return {"ok": False, "detail": "ai response is not a json object", "data": parsed}
        message = str(data.get("message") or "").strip()
        if not message:
            return {"ok": False, "detail": "ai response missing message", "data": data}
        return {"ok": True, "detail": "ok", "data": data}

    def _extract_ai_json(self, parsed):
        if isinstance(parsed, dict) and "message" in parsed:
            return parsed

        if isinstance(parsed, dict):
            content = parsed.get("content")
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") == "text" and part.get("text"):
                        text_parts.append(part.get("text", ""))
                if text_parts:
                    content_text = "".join(text_parts).strip()
                    parsed_text = parse_json_text(content_text)
                    if parsed_text is not None:
                        return parsed_text
                    else:
                        return {"message": content_text}

            choices = parsed.get("choices")
            if isinstance(choices, list) and choices:
                msg = choices[0].get("message", {})
                content = msg.get("content")
                if isinstance(content, list):
                    content = "".join(
                        part.get("text", "") for part in content if isinstance(part, dict)
                    )
                if isinstance(content, str):
                    parsed_text = parse_json_text(content)
                    if parsed_text is not None:
                        return parsed_text
                    else:
                        return {"message": content}
        return parsed
