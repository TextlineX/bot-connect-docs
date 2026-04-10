#!/usr/bin/env python3
import os
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def resolve_role() -> str:
    raw = str(os.getenv("ROBOT_ROLE") or os.getenv("ROBOT_MODE") or "").strip().lower()
    if raw in {"master", "slave"}:
        return raw
    robot_id = str(os.getenv("ROBOT_ID") or "").strip().lower()
    if robot_id.startswith("master"):
        return "master"
    if robot_id.startswith("slave"):
        return "slave"
    return "slave"


def main():
    role = resolve_role()
    target = ROOT / role / "client.py"
    os.environ["ROBOT_ROLE"] = role
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()

