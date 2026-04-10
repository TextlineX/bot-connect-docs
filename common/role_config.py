import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"


def deep_merge(base: dict, extra: dict) -> dict:
    merged = dict(base or {})
    for key, value in (extra or {}).items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def role_config_path(role: str) -> Path:
    safe_role = str(role or "").strip().lower() or "robot"
    return CONFIG_DIR / f"{safe_role}_config.json"


def load_role_config(role: str, defaults: dict | None = None) -> dict:
    path = role_config_path(role)
    base = dict(defaults or {})
    if not path.exists():
        return base
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return base
    if not isinstance(raw, dict):
        return base
    return deep_merge(base, raw)


def save_role_config(role: str, payload: dict):
    path = role_config_path(role)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {}, ensure_ascii=False, indent=2), encoding="utf-8")

