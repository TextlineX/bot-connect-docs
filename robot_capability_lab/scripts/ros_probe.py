from __future__ import annotations

import argparse
import json
import hashlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "robot_capability_lab"
INVENTORY_PATH = LAB_ROOT / "inventory" / "generated" / "interface_inventory.json"
OUTPUT_DIR = LAB_ROOT / "inventory" / "generated"
CASES_ROOT = LAB_ROOT / "cases"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.strip().strip("/")
    value = re.sub(r"[^A-Za-z0-9_]+", "__", value)
    value = re.sub(r"__+", "__", value).strip("_")
    return value or "root"


def folder_name(item: dict) -> str:
    if item["kind"] == "preset_action":
        motion_id = item.get("motion_id", "x")
        area_id = item.get("area_id", "x")
        base = slugify(item.get("data_type", "preset"))
        digest = hashlib.sha1(item["name"].encode("utf-8")).hexdigest()[:8]
        return f"{base}__motion_{motion_id}__area_{area_id}__{digest}"
    slug = slugify(item["name"])
    if slug != "root":
        return slug
    digest = hashlib.sha1(item["name"].encode("utf-8")).hexdigest()[:10]
    return f"item__{digest}"


def run_cmd(args: list[str], timeout: int) -> dict:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "cmd": " ".join(args),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "code": -1,
            "stdout": "",
            "stderr": f"timeout after {timeout}s",
            "cmd": " ".join(args),
        }
    except Exception as exc:
        return {
            "ok": False,
            "code": -1,
            "stdout": "",
            "stderr": str(exc),
            "cmd": " ".join(args),
        }


def case_dir_for(item: dict) -> Path:
    mapping = {
        "topic": "topics",
        "service": "services",
        "preset_action": "actions",
    }
    return CASES_ROOT / mapping.get(item["kind"], "actions") / folder_name(item)


def probe_topic(item: dict, timeout: int, sample_payload: bool) -> dict:
    name = item["name"]
    result = {
        "exists": False,
        "runtime_type": "",
        "info": run_cmd(["ros2", "topic", "info", name, "-v"], timeout),
        "type": run_cmd(["ros2", "topic", "type", name], timeout),
        "interface": None,
        "hz": None,
        "echo": None,
    }
    if result["type"]["ok"] and result["type"]["stdout"]:
        result["exists"] = True
        result["runtime_type"] = result["type"]["stdout"].strip()
        result["interface"] = run_cmd(["ros2", "interface", "show", result["runtime_type"]], timeout)
        result["hz"] = run_cmd(["ros2", "topic", "hz", name], timeout)
        if sample_payload and not item.get("verification", {}).get("skip_payload_echo_by_default"):
            result["echo"] = run_cmd(["ros2", "topic", "echo", name, "--once"], timeout)
        else:
            result["echo"] = {
                "ok": False,
                "code": -1,
                "stdout": "",
                "stderr": "skipped by policy",
                "cmd": "",
            }
    return result


def probe_service(item: dict, timeout: int) -> dict:
    name = item["name"]
    result = {
        "exists": False,
        "runtime_type": "",
        "type": run_cmd(["ros2", "service", "type", name], timeout),
        "interface": None,
        "call": {
            "ok": False,
            "code": -1,
            "stdout": "",
            "stderr": "默认禁用服务调用",
            "cmd": "",
        },
    }
    if result["type"]["ok"] and result["type"]["stdout"]:
        result["exists"] = True
        result["runtime_type"] = result["type"]["stdout"].strip()
        result["interface"] = run_cmd(["ros2", "interface", "show", result["runtime_type"]], timeout)
    return result


def render_summary(items: list[dict]) -> str:
    topic_exists = sum(1 for item in items if item["kind"] == "topic" and item["probe"].get("exists"))
    service_exists = sum(1 for item in items if item["kind"] == "service" and item["probe"].get("exists"))
    lines = [
        "# 真机探测摘要",
        "",
        f"- 生成时间: `{now_iso()}`",
        f"- 探测项总数: `{len(items)}`",
        f"- 发现话题数: `{topic_exists}`",
        f"- 发现服务数: `{service_exists}`",
        "",
        "| Kind | Name | Exists | Runtime Type | Project |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            "| {kind} | `{name}` | {exists} | `{runtime_type}` | {project_status} |".format(
                kind=item["kind"],
                name=item["name"],
                exists="yes" if item["probe"].get("exists") else "no",
                runtime_type=item["probe"].get("runtime_type", "") or "-",
                project_status=item["project_status"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="探测机器人 ROS2 话题与服务")
    parser.add_argument("--timeout", type=int, default=5, help="单个 ros2 命令超时秒数")
    parser.add_argument(
        "--sample-payload",
        action="store_true",
        help="对低风险话题尝试 echo --once，高带宽话题仍默认跳过",
    )
    args = parser.parse_args()

    if shutil.which("ros2") is None:
        raise SystemExit("未找到 ros2 命令，请在已 source ROS2/AimDK 环境的机器上执行。")

    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    items_out: list[dict] = []
    for item in payload.get("items", []):
        if item["kind"] == "topic":
            probe = probe_topic(item, args.timeout, args.sample_payload)
        elif item["kind"] == "service":
            probe = probe_service(item, args.timeout)
        else:
            probe = {
                "exists": False,
                "runtime_type": "",
                "note": "预设动作依附于 SetMcPresetMotion 服务，需结合 service case 测试",
            }
        enriched = dict(item)
        enriched["probe"] = probe
        items_out.append(enriched)

        folder = case_dir_for(item)
        if folder.exists():
            (folder / "runtime.json").write_text(
                json.dumps(
                    {
                        "generated_at": now_iso(),
                        "item": item["name"],
                        "kind": item["kind"],
                        "probe": probe,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

    snapshot = {
        "generated_at": now_iso(),
        "items": items_out,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "runtime_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "runtime_summary.md").write_text(
        render_summary(items_out),
        encoding="utf-8",
    )
    print(f"[probe] wrote snapshot for {len(items_out)} items")


if __name__ == "__main__":
    main()
