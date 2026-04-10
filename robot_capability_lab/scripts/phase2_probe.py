from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from ros_probe import case_dir_for, now_iso, run_cmd


ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "robot_capability_lab"
PLAN_PATH = LAB_ROOT / "config" / "phase2_plan.json"
INVENTORY_PATH = LAB_ROOT / "inventory" / "generated" / "interface_inventory.json"
OUTPUT_DIR = LAB_ROOT / "inventory" / "generated"


def load_inventory() -> dict[tuple[str, str], dict]:
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return {(item["kind"], item["name"]): item for item in payload.get("items", [])}


def load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def service_type(service_name: str, timeout: int) -> dict:
    return run_cmd(["ros2", "service", "type", service_name], timeout)


def topic_type(topic_name: str, timeout: int) -> dict:
    return run_cmd(["ros2", "topic", "type", topic_name], timeout)


def skipped_probe(reason: str) -> dict:
    return {
        "ok": False,
        "code": -1,
        "stdout": "",
        "stderr": reason,
        "cmd": "",
    }


def call_service(
    service_name: str,
    request: dict,
    timeout: int,
    retries: int,
    retry_interval: float,
) -> dict:
    type_result = service_type(service_name, timeout)
    if not type_result["ok"] or not type_result["stdout"]:
        return {
            "ok": False,
            "code": -1,
            "stdout": "",
            "stderr": "service type unavailable",
            "cmd": "",
            "service_type": "",
            "request": request or {},
            "attempts": [],
        }
    srv_type = type_result["stdout"].strip()
    request_json = json.dumps(request or {}, ensure_ascii=False)
    attempts: list[dict] = []
    total_retries = max(1, retries)
    for attempt in range(1, total_retries + 1):
        result = run_cmd(["ros2", "service", "call", service_name, srv_type, request_json], timeout)
        result["attempt"] = attempt
        attempts.append(result)
        if result["ok"]:
            break
        if attempt < total_retries and retry_interval > 0:
            time.sleep(retry_interval)
    final = dict(attempts[-1])
    final["service_type"] = srv_type
    final["request"] = request or {}
    final["attempts"] = attempts
    return final


def sample_topic(topic_name: str, timeout: int, echo_retries: int, retry_interval: float) -> dict:
    type_result = topic_type(topic_name, timeout)
    result = {
        "exists": False,
        "runtime_type": "",
        "type": type_result,
        "info": run_cmd(["ros2", "topic", "info", topic_name, "-v"], timeout),
        "echo": None,
        "interface": None,
    }
    if not type_result["ok"] or not type_result["stdout"]:
        result["echo"] = skipped_probe("topic type unavailable")
        result["echo"]["attempts"] = []
        return result
    result["exists"] = True
    result["runtime_type"] = type_result["stdout"].strip()
    result["interface"] = run_cmd(["ros2", "interface", "show", result["runtime_type"]], timeout)
    attempts: list[dict] = []
    total_retries = max(1, echo_retries)
    for attempt in range(1, total_retries + 1):
        echo_result = run_cmd(["ros2", "topic", "echo", topic_name, "--once"], timeout)
        echo_result["attempt"] = attempt
        attempts.append(echo_result)
        if echo_result["ok"]:
            break
        if attempt < total_retries and retry_interval > 0:
            time.sleep(retry_interval)
    result["echo"] = dict(attempts[-1])
    result["echo"]["attempts"] = attempts
    return result


def write_case_payload(inventory: dict[tuple[str, str], dict], kind: str, name: str, payload: dict) -> None:
    item = inventory.get((kind, name))
    if not item:
        return
    folder = case_dir_for(item)
    if not folder.exists():
        return
    (folder / "phase2.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def summarize(
    topic_results: list[dict],
    query_results: list[dict],
    side_effect_results: list[dict],
    allow_side_effects: bool,
) -> str:
    topic_ok = sum(1 for item in topic_results if item["probe"].get("echo", {}).get("ok"))
    query_ok = sum(1 for item in query_results if item["probe"].get("ok"))
    side_ok = sum(1 for item in side_effect_results if not item.get("skipped") and item["probe"].get("ok"))
    side_run = sum(1 for item in side_effect_results if not item.get("skipped"))
    side_total = len(side_effect_results)
    lines = [
        "# 二阶段测试摘要",
        "",
        f"- 生成时间: `{now_iso()}`",
        f"- 话题采样成功: `{topic_ok}/{len(topic_results)}`",
        f"- 查询服务成功: `{query_ok}/{len(query_results)}`",
        f"- 副作用测试: `{'开启' if allow_side_effects else '关闭'}`",
        (
            f"- 副作用成功: `{side_ok}/{side_run}`"
            if allow_side_effects
            else f"- 副作用测试默认跳过，计划项: `{side_total}`"
        ),
        "",
        "## 话题采样",
        "",
    ]
    for item in topic_results:
        probe = item["probe"]
        status = "ok" if probe.get("echo", {}).get("ok") else "fail"
        lines.append(f"- `{item['name']}` | {status} | `{probe.get('runtime_type', '') or '-'}`")
    lines.extend(["", "## 查询服务", ""])
    for item in query_results:
        probe = item["probe"]
        status = "ok" if probe.get("ok") else "fail"
        lines.append(f"- `{item['name']}` | {status} | `{probe.get('service_type', '') or '-'}`")
    lines.extend(["", "## 副作用测试", ""])
    if not allow_side_effects:
        for item in side_effect_results:
            lines.append(f"- `{item['name']}` | skipped | `-`")
    else:
        for item in side_effect_results:
            probe = item["probe"]
            status = "ok" if probe.get("ok") else "fail"
            lines.append(f"- `{item['name']}` | {status} | `{probe.get('service_type', '') or '-'}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="机器人能力实验室二阶段测试")
    parser.add_argument("--allow-side-effects", action="store_true", help="允许执行有副作用的主动调用测试")
    parser.add_argument("--timeout", type=int, default=8, help="默认超时秒数")
    parser.add_argument("--service-retries", type=int, default=3, help="服务调用重试次数")
    parser.add_argument("--echo-retries", type=int, default=2, help="话题采样重试次数")
    parser.add_argument("--retry-interval", type=float, default=0.35, help="重试间隔秒数")
    args = parser.parse_args()

    if shutil.which("ros2") is None:
        raise SystemExit("未找到 ros2 命令，请在已 source ROS2/AimDK 环境的机器上执行。")

    inventory = load_inventory()
    plan = load_plan()

    topic_results: list[dict] = []
    for topic_test in plan.get("topic_tests", []):
        timeout = int(topic_test.get("timeout") or args.timeout)
        probe = sample_topic(topic_test["name"], timeout, args.echo_retries, args.retry_interval)
        payload = {
            "generated_at": now_iso(),
            "stage": "phase2",
            "kind": "topic",
            "name": topic_test["name"],
            "notes": topic_test.get("notes", ""),
            "probe": probe,
        }
        write_case_payload(inventory, "topic", topic_test["name"], payload)
        topic_results.append({"name": topic_test["name"], "notes": topic_test.get("notes", ""), "probe": probe})

    query_results: list[dict] = []
    for service_test in plan.get("service_query_tests", []):
        timeout = int(service_test.get("timeout") or args.timeout)
        probe = call_service(
            service_test["name"],
            service_test.get("request", {}),
            timeout,
            args.service_retries,
            args.retry_interval,
        )
        payload = {
            "generated_at": now_iso(),
            "stage": "phase2",
            "kind": "service_query",
            "name": service_test["name"],
            "notes": service_test.get("notes", ""),
            "probe": probe,
        }
        write_case_payload(inventory, "service", service_test["name"], payload)
        query_results.append({"name": service_test["name"], "notes": service_test.get("notes", ""), "probe": probe})

    side_effect_results: list[dict] = []
    if args.allow_side_effects:
        for service_test in plan.get("service_side_effect_tests", []):
            timeout = int(service_test.get("timeout") or args.timeout)
            probe = call_service(
                service_test["name"],
                service_test.get("request", {}),
                timeout,
                args.service_retries,
                args.retry_interval,
            )
            payload = {
                "generated_at": now_iso(),
                "stage": "phase2",
                "kind": "service_side_effect",
                "name": service_test["name"],
                "notes": service_test.get("notes", ""),
                "probe": probe,
            }
            write_case_payload(inventory, "service", service_test["name"], payload)
            side_effect_results.append(
                {
                    "name": service_test["name"],
                    "notes": service_test.get("notes", ""),
                    "probe": probe,
                    "skipped": False,
                }
            )
    else:
        for service_test in plan.get("service_side_effect_tests", []):
            probe = skipped_probe("skipped by policy: allow-side-effects disabled")
            payload = {
                "generated_at": now_iso(),
                "stage": "phase2",
                "kind": "service_side_effect",
                "name": service_test["name"],
                "notes": service_test.get("notes", ""),
                "probe": probe,
            }
            write_case_payload(inventory, "service", service_test["name"], payload)
            side_effect_results.append(
                {
                    "name": service_test["name"],
                    "notes": service_test.get("notes", ""),
                    "probe": probe,
                    "skipped": True,
                }
            )

    summary_payload = {
        "generated_at": now_iso(),
        "allow_side_effects": args.allow_side_effects,
        "topic_results": topic_results,
        "query_results": query_results,
        "side_effect_results": side_effect_results,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "phase2_snapshot.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "phase2_summary.md").write_text(
        summarize(topic_results, query_results, side_effect_results, args.allow_side_effects),
        encoding="utf-8",
    )
    print(
        f"[phase2] topic={len(topic_results)} query={len(query_results)} "
        f"side_effect={sum(1 for item in side_effect_results if not item.get('skipped'))} "
        f"allow_side_effects={args.allow_side_effects}"
    )


if __name__ == "__main__":
    main()
