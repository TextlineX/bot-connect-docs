from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "robot_capability_lab"
INVENTORY_PATH = LAB_ROOT / "inventory" / "generated" / "interface_inventory.json"
CASES_ROOT = LAB_ROOT / "cases"


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


def case_root(kind: str) -> Path:
    if kind == "topic":
        return CASES_ROOT / "topics"
    if kind == "service":
        return CASES_ROOT / "services"
    return CASES_ROOT / "actions"


def command_block(item: dict) -> list[str]:
    name = item["name"]
    data_type = item.get("data_type", "")
    lines: list[str] = []
    if item["kind"] == "topic":
        lines.append(f"ros2 topic info {name} -v")
        lines.append(f"ros2 topic type {name}")
        if data_type:
            lines.append(f"ros2 interface show {data_type}")
        if item.get("verification", {}).get("skip_payload_echo_by_default"):
            lines.append(f"# 高带宽话题，默认先跑: ros2 topic hz {name}")
            lines.append(f"# 若确认安全，再手工采样: ros2 topic echo {name} --once")
        else:
            lines.append(f"ros2 topic echo {name} --once")
            lines.append(f"ros2 topic hz {name}")
    elif item["kind"] == "service":
        lines.append(f"ros2 service type {name}")
        if data_type:
            lines.append(f"ros2 interface show {data_type}")
        lines.append("# 默认只查类型和结构，真实调用前先确认安全")
    else:
        lines.append("# 预设动作项请结合 SetMcPresetMotion 服务测试")
    return lines


def render_readme(item: dict) -> str:
    lines = [
        f"# {item['kind']} 测试项",
        "",
        f"- 名称: `{item['name']}`",
        f"- 分类: `{item['category']}`",
        f"- 类型: `{item.get('data_type', '') or '待确认'}`",
        f"- 文档状态: `{item['doc_status']}`",
        f"- 项目状态: `{item['project_status']}`",
        "",
        "## 文档来源",
        "",
    ]
    for source in item.get("sources", []):
        section = source.get("section", "") or "未标注章节"
        lines.append(f"- `{source['path']}` | {section}")
    lines.extend(
        [
            "",
            "## 推荐命令",
            "",
            "```bash",
            *command_block(item),
            "```",
            "",
            "## 测试记录",
            "",
            "- 首次验证时间: ",
            "- 机器人环境: ",
            "- 是否存在: ",
            "- 实际类型: ",
            "- QoS / 频率: ",
            "- 样本是否拿到: ",
            "- 结论: ",
            "- 备注: ",
            "",
        ]
    )
    if item["kind"] == "preset_action":
        lines.extend(
            [
                "## 动作参数",
                "",
                f"- motion_id: `{item.get('motion_id')}`",
                f"- area_id: `{item.get('area_id')}`",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    for item in payload.get("items", []):
        folder = case_root(item["kind"]) / folder_name(item)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "case.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        readme_path = folder / "README.md"
        if not readme_path.exists():
            readme_path.write_text(render_readme(item), encoding="utf-8")
    print(f"[cases] generated {len(payload.get('items', []))} case folders")


if __name__ == "__main__":
    main()
