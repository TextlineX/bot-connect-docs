from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "robot_capability_lab"
KB_ROOT = ROOT / "知识库"
OUTPUT_DIR = LAB_ROOT / "inventory" / "generated"
PROJECT_BINDINGS_PATH = LAB_ROOT / "config" / "project_bindings.json"

TOPIC_TABLE_HEADER = "话题名称 | 数据类型"
SERVICE_TABLE_HEADER = "服务名称 | 数据类型"
PRESET_TABLE_HEADER = "动作名称 | `motion` | `area`"

SERVICE_BLOCK_RE = re.compile(r"# 服务名称:\s*(/[\w/\-.]+)")
TOPIC_BLOCK_RE = re.compile(r"# 话题名称:\s*(/[\w/\-.\[\]]+)")
ARROW_RE = re.compile(r"`(?P<name>/[^`]+)`\s*[→-]+\s*`(?P<dtype>[^`]+)`")


@dataclass
class SourceRef:
    path: str
    section: str
    description: str


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_type(value: str) -> str:
    value = (value or "").strip().strip("`")
    if not value or value in {"-", "N/A"}:
        return ""
    builtin = {
        "Imu": "sensor_msgs/msg/Imu",
        "Image": "sensor_msgs/msg/Image",
        "CompressedImage": "sensor_msgs/msg/CompressedImage",
        "PointCloud2": "sensor_msgs/msg/PointCloud2",
        "CameraInfo": "sensor_msgs/msg/CameraInfo",
    }
    return builtin.get(value, value)


def infer_category(name: str, source_path: str = "") -> str:
    lower_name = name.lower()
    lower_source = source_path.lower()
    if "playtts" in lower_name or "volume" in lower_name or "mute" in lower_name:
        return "voice"
    if "audio" in lower_name or "process_audio_output" in lower_name:
        return "audio"
    if "face" in lower_name or "emoji" in lower_name or "video" in lower_name or "screen" in lower_source:
        return "screen"
    if "light" in lower_name or "lights" in lower_source:
        return "lights"
    if "pmu" in lower_name or "battery" in lower_name:
        return "power"
    if "lidar" in lower_name:
        return "lidar"
    if "imu" in lower_name:
        return "imu"
    if "touch" in lower_name:
        return "touch"
    if "camera" in lower_name or "image" in lower_name or "rgbd" in lower_name or "stereo" in lower_name:
        return "vision"
    if "joint" in lower_name:
        return "joint"
    if "hand" in lower_name or "gripper" in lower_name or "endeffector" in lower_source:
        return "endeffector"
    if "mc" in lower_name or "locomotion" in lower_name or "motion" in lower_name:
        return "motion"
    return "other"


def infer_doc_status(source_path: str, section: str, description: str) -> str:
    merged = f"{source_path} {section} {description}"
    if "待开放" in merged:
        return "待开放"
    if "待发布" in merged:
        return "待发布"
    if "实测" in merged:
        return "实测"
    if "未现场确认" in merged:
        return "未确认"
    return "已文档化"


def is_high_bandwidth(name: str, data_type: str) -> bool:
    merged = f"{name} {data_type}".lower()
    patterns = ["image", "compressedimage", "pointcloud2", "lidar", "audio", "camera"]
    return any(pattern in merged for pattern in patterns)


def parse_table_rows(text: str, path: Path) -> list[dict]:
    items: list[dict] = []
    lines = text.splitlines()
    current_section = ""
    mode = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip()
            mode = ""
            continue
        if TOPIC_TABLE_HEADER in stripped:
            mode = "topic"
            continue
        if SERVICE_TABLE_HEADER in stripped:
            mode = "service"
            continue
        if PRESET_TABLE_HEADER in stripped:
            mode = "preset_action"
            continue
        if not mode:
            continue
        if not stripped or stripped.startswith("---"):
            continue
        if "|" not in stripped:
            if mode != "preset_action":
                mode = ""
            continue
        columns = [column.strip() for column in line.split("|")]
        if len(columns) < 3:
            continue
        if mode in {"topic", "service"}:
            name = columns[0].strip("` ")
            if not name.startswith("/"):
                continue
            description = columns[2].strip("` ")
            items.append(
                {
                    "kind": mode,
                    "name": name,
                    "data_type": normalize_type(columns[1]),
                    "description": description,
                    "source_path": rel(path),
                    "section": current_section,
                    "doc_status": infer_doc_status(rel(path), current_section, description),
                }
            )
        elif mode == "preset_action" and len(columns) >= 4:
            action_name = columns[0].strip("` ")
            motion_id = columns[1].strip("` ")
            area_id = columns[2].strip("` ")
            description = columns[3].strip("` ")
            if not action_name or not motion_id.isdigit() or not area_id.isdigit():
                continue
            items.append(
                {
                    "kind": "preset_action",
                    "name": action_name,
                    "data_type": "SetMcPresetMotion",
                    "description": description,
                    "motion_id": int(motion_id),
                    "area_id": int(area_id),
                    "source_path": rel(path),
                    "section": current_section,
                    "doc_status": infer_doc_status(rel(path), current_section, description),
                }
            )
    return items


def parse_inline_refs(text: str, path: Path) -> list[dict]:
    items: list[dict] = []
    current_section = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip()
        arrow_match = ARROW_RE.search(line)
        if arrow_match:
            name = arrow_match.group("name").strip()
            items.append(
                {
                    "kind": "service" if "/srv/" in name else "topic",
                    "name": name,
                    "data_type": normalize_type(arrow_match.group("dtype")),
                    "description": stripped,
                    "source_path": rel(path),
                    "section": current_section,
                    "doc_status": infer_doc_status(rel(path), current_section, stripped),
                }
            )
        for regex, kind in ((SERVICE_BLOCK_RE, "service"), (TOPIC_BLOCK_RE, "topic")):
            block_match = regex.search(line)
            if not block_match:
                continue
            items.append(
                {
                    "kind": kind,
                    "name": block_match.group(1).strip(),
                    "data_type": "",
                    "description": stripped,
                    "source_path": rel(path),
                    "section": current_section,
                    "doc_status": infer_doc_status(rel(path), current_section, stripped),
                }
            )
    return items


def load_project_bindings() -> dict[tuple[str, str], list[dict]]:
    raw = json.loads(read_text(PROJECT_BINDINGS_PATH))
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for binding in raw.get("bindings", []):
        grouped[(binding.get("kind", ""), binding.get("interface_name", ""))].append(binding)
    return grouped


def doc_status_rank(value: str) -> int:
    order = {
        "已文档化": 1,
        "实测": 2,
        "未确认": 3,
        "待开放": 4,
        "待发布": 5,
    }
    return order.get(value, 0)


def merge_items(items: list[dict], bindings: dict[tuple[str, str], list[dict]]) -> list[dict]:
    grouped: dict[tuple[str, str], dict] = {}
    for item in items:
        key = (item["kind"], item["name"])
        source = SourceRef(
            path=item["source_path"],
            section=item.get("section", ""),
            description=item.get("description", ""),
        )
        if key not in grouped:
            grouped[key] = {
                "id": f"{item['kind']}:{item['name']}",
                "kind": item["kind"],
                "name": item["name"],
                "data_type": item.get("data_type", ""),
                "category": "motion" if item["kind"] == "preset_action" else infer_category(item["name"], item["source_path"]),
                "doc_status": item.get("doc_status", "已文档化"),
                "sources": [],
            }
            if item["kind"] == "preset_action":
                grouped[key]["motion_id"] = item.get("motion_id")
                grouped[key]["area_id"] = item.get("area_id")
        entry = grouped[key]
        if not entry.get("data_type") and item.get("data_type"):
            entry["data_type"] = item["data_type"]
        if doc_status_rank(item.get("doc_status", "")) > doc_status_rank(entry["doc_status"]):
            entry["doc_status"] = item["doc_status"]
        entry["sources"].append(source.__dict__)

    merged: list[dict] = []
    priority = {
        "implemented": 4,
        "partial": 3,
        "needs_real_adapter": 2,
        "not_connected": 1,
    }
    for key, entry in sorted(grouped.items(), key=lambda pair: (pair[1]["kind"], pair[1]["category"], pair[1]["name"])):
        matched_bindings = bindings.get(key, [])
        project_status = "not_connected"
        if matched_bindings:
            project_status = max(
                [binding.get("project_status", "not_connected") for binding in matched_bindings],
                key=lambda value: priority.get(value, 0),
            )
        entry["project_status"] = project_status
        entry["project_bindings"] = matched_bindings
        entry["verification"] = {
            "needs_runtime_validation": True,
            "high_bandwidth": is_high_bandwidth(entry["name"], entry.get("data_type", "")),
            "skip_payload_echo_by_default": is_high_bandwidth(entry["name"], entry.get("data_type", "")),
        }
        merged.append(entry)
    return merged


def build_gap_report(items: list[dict]) -> str:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        buckets[item["project_status"]].append(item)

    def render_bucket(title: str, status: str) -> list[str]:
        lines = [f"## {title}", ""]
        subset = sorted(buckets.get(status, []), key=lambda value: (value["category"], value["name"]))
        if not subset:
            lines.append("- 无")
            lines.append("")
            return lines
        for item in subset:
            lines.append(
                f"- `{item['name']}` | {item['kind']} | {item['category']} | {item.get('data_type', '') or '类型待确认'}"
            )
        lines.append("")
        return lines

    lines = [
        "# 项目能力缺口对照",
        "",
        f"- 生成时间: `{now_iso()}`",
        f"- 接口总数: `{len(items)}`",
        f"- 真实已接入: `{len(buckets.get('implemented', []))}`",
        f"- 半接入/代理: `{len(buckets.get('partial', []))}`",
        f"- 需要真实 ROS 适配: `{len(buckets.get('needs_real_adapter', []))}`",
        f"- 完全未接入: `{len(buckets.get('not_connected', []))}`",
        "",
        "## 重点结论",
        "",
        "- 当前项目真正接到机器人原生 ROS2 的核心能力主要是 `PlayTts` 和 `SetMcPresetMotion`。",
        "- 运动、麦克风、相机、Lidar、IMU、触摸、PMU、屏幕等接口仍需按 case 逐项验证。",
        "- 尤其相机和高带宽传感器，知识库有文档不等于项目已经能用，必须上真机跑探测。",
        "",
    ]
    lines.extend(render_bucket("已真实桥接", "implemented"))
    lines.extend(render_bucket("半接入或代理", "partial"))
    lines.extend(render_bucket("已有入口但缺真实 ROS 适配", "needs_real_adapter"))
    lines.extend(render_bucket("知识库存在但项目未接入", "not_connected"))
    return "\n".join(lines).strip() + "\n"


def build_inventory_markdown(items: list[dict]) -> str:
    lines = [
        "# 接口清单",
        "",
        f"- 生成时间: `{now_iso()}`",
        f"- 接口总数: `{len(items)}`",
        "",
        "| Kind | Name | Type | Category | Doc | Project |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            "| {kind} | `{name}` | `{dtype}` | {category} | {doc_status} | {project_status} |".format(
                kind=item["kind"],
                name=item["name"],
                dtype=item.get("data_type", "") or "-",
                category=item["category"],
                doc_status=item["doc_status"],
                project_status=item["project_status"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bindings = load_project_bindings()
    raw_items: list[dict] = []
    for path in sorted(KB_ROOT.rglob("*.md")):
        text = read_text(path)
        raw_items.extend(parse_table_rows(text, path))
        raw_items.extend(parse_inline_refs(text, path))

    merged_items = merge_items(raw_items, bindings)
    payload = {
        "generated_at": now_iso(),
        "counts": {
            "total": len(merged_items),
            "topics": sum(1 for item in merged_items if item["kind"] == "topic"),
            "services": sum(1 for item in merged_items if item["kind"] == "service"),
            "preset_actions": sum(1 for item in merged_items if item["kind"] == "preset_action"),
        },
        "items": merged_items,
    }

    (OUTPUT_DIR / "interface_inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "interface_inventory.md").write_text(
        build_inventory_markdown(merged_items),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "project_gap_report.md").write_text(
        build_gap_report(merged_items),
        encoding="utf-8",
    )
    print(f"[inventory] generated {len(merged_items)} items")


if __name__ == "__main__":
    main()
