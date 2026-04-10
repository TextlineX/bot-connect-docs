#!/usr/bin/env bash
set -euo pipefail

# 在机器人上执行能力探测
# 预期运行位置：
#   /agibot/data/home/agi/bot_connect
#
# 用法：
#   bash robot_capability_lab/scripts/run_probe_remote.sh
#   PYTHON_BIN=python3 bash robot_capability_lab/scripts/run_probe_remote.sh --sample-payload
#   PYTHON_BIN=python3 bash robot_capability_lab/scripts/run_probe_remote.sh --phase2
#   PYTHON_BIN=python3 bash robot_capability_lab/scripts/run_probe_remote.sh --all-phases --allow-side-effects

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
AIMDK_SETUP="${AIMDK_SETUP:-/agibot/data/home/agi/aimdk/install/setup.bash}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_PHASE1=1
RUN_PHASE2=0
PHASE_EXPLICIT=0
PHASE1_ARGS=()
PHASE2_ARGS=()

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
      PHASE1_ARGS+=(--sample-payload)
      ;;
    --allow-side-effects)
      PHASE2_ARGS+=(--allow-side-effects)
      ;;
    --timeout)
      if [ "$#" -lt 2 ]; then
        echo "--timeout 缺少参数" >&2
        exit 1
      fi
      PHASE1_ARGS+=(--timeout "$2")
      PHASE2_ARGS+=(--timeout "$2")
      shift
      ;;
    --service-retries|--echo-retries|--retry-interval)
      if [ "$#" -lt 2 ]; then
        echo "$1 缺少参数" >&2
        exit 1
      fi
      PHASE2_ARGS+=("$1" "$2")
      shift
      ;;
    *)
      echo "未知参数: $1" >&2
      exit 1
      ;;
  esac
  shift
done

# Avoid unbound variable issues inside ROS setup scripts when running with `set -u`
export AMENT_TRACE_SETUP_FILES="${AMENT_TRACE_SETUP_FILES:-0}"
PY3_BIN="$(command -v python3 || true)"
if [ -z "$PY3_BIN" ]; then
  PY3_BIN="/usr/bin/python3"
fi
export AMENT_PYTHON_EXECUTABLE="${AMENT_PYTHON_EXECUTABLE:-$PY3_BIN}"
export COLCON_TRACE="${COLCON_TRACE:-0}"
export COLCON_PYTHON_EXECUTABLE="${COLCON_PYTHON_EXECUTABLE:-$PY3_BIN}"

if [ -f "$ROS_SETUP" ]; then
  # shellcheck disable=SC1090
  source "$ROS_SETUP"
else
  echo "未找到 ROS 环境: $ROS_SETUP" >&2
  exit 1
fi

if [ -f "$AIMDK_SETUP" ]; then
  # shellcheck disable=SC1090
  source "$AIMDK_SETUP"
fi

cd "$ROOT"

echo "[probe-remote] ROOT=$ROOT"
echo "[probe-remote] PYTHON_BIN=$PYTHON_BIN"
echo "[probe-remote] RUN_PHASE1=$RUN_PHASE1 RUN_PHASE2=$RUN_PHASE2"

if [ "$RUN_PHASE1" -eq 1 ]; then
  "$PYTHON_BIN" robot_capability_lab/scripts/ros_probe.py "${PHASE1_ARGS[@]}"
fi

if [ "$RUN_PHASE2" -eq 1 ]; then
  "$PYTHON_BIN" robot_capability_lab/scripts/phase2_probe.py "${PHASE2_ARGS[@]}"
fi
