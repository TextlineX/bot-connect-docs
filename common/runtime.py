from __future__ import annotations

from typing import Callable, Dict, Tuple

from role_config import load_role_config, save_role_config, deep_merge


def build_runtime(role: str, defaults: Dict | None = None) -> Tuple[Dict, Callable[[], Dict], Callable[[Dict], Dict]]:
    """
    创建角色运行态：
      - state 持久化到 config/{role}_config.json
      - config_provider 返回当前 config_version
      - on_config_sync 落盘 role_config 并返回确认
    """
    state: Dict = load_role_config(role, defaults or {})

    def config_provider() -> Dict:
        try:
            version = int(state.get("config_version") or 0)
        except Exception:
            version = 0
        return {"config_version": version}

    def on_config_sync(data: Dict) -> Dict:
        payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        role_cfg = payload.get("role_config") if isinstance(payload.get("role_config"), dict) else {}
        version = payload.get("version", data.get("config_version", state.get("config_version", 0)))
        merged = deep_merge(state, role_cfg)
        try:
            merged["config_version"] = int(version or merged.get("config_version") or 0)
        except Exception:
            merged["config_version"] = merged.get("config_version") or 0
        state.clear()
        state.update(merged)
        save_role_config(role, merged)
        return {"saved": True, "config_version": merged.get("config_version", 0)}

    return state, config_provider, on_config_sync

