#!/usr/bin/env bash
set -euo pipefail

# 一键：本地生成清单 -> 同步到机器人 -> 机器人执行探测 -> 拉回摘要
#
# 用法：
#   ./scripts/run_robot_capability_lab.sh
#   ./scripts/run_robot_capability_lab.sh agi@192.168.88.88 /agibot/data/home/agi/bot_connect
#   SAMPLE_PAYLOAD=1 ./scripts/run_robot_capability_lab.sh
#   ./scripts/run_robot_capability_lab.sh --phase2
#   ./scripts/run_robot_capability_lab.sh --all-phases --allow-side-effects

ROBOT_HOST="agi@192.168.88.88"
REMOTE_BASE="/agibot/data/home/agi/bot_connect"
PYTHON_BIN="${PYTHON_BIN:-python}"
REMOTE_PYTHON_BIN="${REMOTE_PYTHON_BIN:-python3}"
SAMPLE_PAYLOAD="${SAMPLE_PAYLOAD:-0}"
RUN_PHASE1="${RUN_PHASE1:-1}"
RUN_PHASE2="${RUN_PHASE2:-0}"
ALLOW_SIDE_EFFECTS="${ALLOW_SIDE_EFFECTS:-0}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB_DIR="$ROOT/robot_capability_lab"
REMOTE_LAB_DIR="${REMOTE_BASE%/}/robot_capability_lab"

POSITIONAL=()
PHASE_EXPLICIT=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --phase1)
      if [ "$PHASE_EXPLICIT" -eq 0 ]; then
        RUN_PHASE1=1
        RUN_PHASE2=0
        PHASE_EXPLICIT=1
      else
        RUN_PHASE1=1
      fi
      ;;
    --phase2)
      if [ "$PHASE_EXPLICIT" -eq 0 ]; then
        RUN_PHASE1=0
        RUN_PHASE2=1
        PHASE_EXPLICIT=1
      else
        RUN_PHASE2=1
      fi
      ;;
    --all-phases)
      RUN_PHASE1=1
      RUN_PHASE2=1
      PHASE_EXPLICIT=1
      ;;
    --sample-payload)
      SAMPLE_PAYLOAD=1
      ;;
    --allow-side-effects)
      ALLOW_SIDE_EFFECTS=1
      ;;
    *)
      POSITIONAL+=("$1")
      ;;
  esac
  shift
done

if [ "${#POSITIONAL[@]}" -ge 1 ]; then
  ROBOT_HOST="${POSITIONAL[0]}"
fi
if [ "${#POSITIONAL[@]}" -ge 2 ]; then
  REMOTE_BASE="${POSITIONAL[1]}"
fi
if [ "${#POSITIONAL[@]}" -gt 2 ]; then
  echo "位置参数最多只支持 robot_host 和 remote_base" >&2
  exit 1
fi

if [ "$RUN_PHASE1" != "1" ] && [ "$RUN_PHASE2" != "1" ]; then
  echo "至少需要启用一个阶段：--phase1 / --phase2 / --all-phases" >&2
  exit 1
fi

REMOTE_LAB_DIR="${REMOTE_BASE%/}/robot_capability_lab"

echo "[lab] 生成本地接口清单"
"$PYTHON_BIN" "$ROOT/robot_capability_lab/scripts/build_inventory.py"
"$PYTHON_BIN" "$ROOT/robot_capability_lab/scripts/generate_case_folders.py"

echo "[lab] 同步到机器人: $ROBOT_HOST"
"$ROOT/scripts/sync_robot_capability_lab.sh" "$ROBOT_HOST" "$REMOTE_BASE"

REMOTE_ARGS=()
if [ "$RUN_PHASE1" = "1" ]; then
  REMOTE_ARGS+=(--phase1)
fi
if [ "$RUN_PHASE2" = "1" ]; then
  REMOTE_ARGS+=(--phase2)
fi
if [ "$SAMPLE_PAYLOAD" = "1" ]; then
  REMOTE_ARGS+=(--sample-payload)
fi
if [ "$ALLOW_SIDE_EFFECTS" = "1" ]; then
  REMOTE_ARGS+=(--allow-side-effects)
fi

echo "[lab] 远端执行探测"
ssh "$ROBOT_HOST" "cd '$REMOTE_BASE' && PYTHON_BIN='$REMOTE_PYTHON_BIN' bash robot_capability_lab/scripts/run_probe_remote.sh ${REMOTE_ARGS[*]:-}"

echo "[lab] 拉回结果文件"
if [ "$RUN_PHASE1" = "1" ]; then
  scp "$ROBOT_HOST:$REMOTE_LAB_DIR/inventory/generated/runtime_snapshot.json" "$LAB_DIR/inventory/generated/runtime_snapshot.json"
  scp "$ROBOT_HOST:$REMOTE_LAB_DIR/inventory/generated/runtime_summary.md" "$LAB_DIR/inventory/generated/runtime_summary.md"
fi
if [ "$RUN_PHASE2" = "1" ]; then
  scp "$ROBOT_HOST:$REMOTE_LAB_DIR/inventory/generated/phase2_snapshot.json" "$LAB_DIR/inventory/generated/phase2_snapshot.json"
  scp "$ROBOT_HOST:$REMOTE_LAB_DIR/inventory/generated/phase2_summary.md" "$LAB_DIR/inventory/generated/phase2_summary.md"
fi
scp -r "$ROBOT_HOST:$REMOTE_LAB_DIR/cases/topics" "$LAB_DIR/cases"
scp -r "$ROBOT_HOST:$REMOTE_LAB_DIR/cases/services" "$LAB_DIR/cases"
scp -r "$ROBOT_HOST:$REMOTE_LAB_DIR/cases/actions" "$LAB_DIR/cases"

echo "[lab] 完成"
if [ "$RUN_PHASE1" = "1" ]; then
  echo "  一阶段摘要: $LAB_DIR/inventory/generated/runtime_summary.md"
  echo "  一阶段快照: $LAB_DIR/inventory/generated/runtime_snapshot.json"
fi
if [ "$RUN_PHASE2" = "1" ]; then
  echo "  二阶段摘要: $LAB_DIR/inventory/generated/phase2_summary.md"
  echo "  二阶段快照: $LAB_DIR/inventory/generated/phase2_snapshot.json"
fi
