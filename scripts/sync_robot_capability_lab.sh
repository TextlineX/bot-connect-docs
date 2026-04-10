#!/usr/bin/env bash
set -euo pipefail

# 将 robot_capability_lab 同步到机器人
# 默认目标：
#   agi@192.168.88.88:/agibot/data/home/agi/bot_connect/robot_capability_lab
#
# 用法：
#   ./scripts/sync_robot_capability_lab.sh
#   ./scripts/sync_robot_capability_lab.sh agi@192.168.88.88
#   ./scripts/sync_robot_capability_lab.sh agi@192.168.88.88 /agibot/data/home/agi/bot_connect
#
# 依赖：
#   ssh
#   rsync

ROBOT_HOST="${1:-agi@192.168.88.88}"
REMOTE_BASE="${2:-/agibot/data/home/agi/bot_connect}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT/robot_capability_lab/"
DEST_DIR="${REMOTE_BASE%/}/robot_capability_lab"

if [ ! -d "$SRC_DIR" ]; then
  echo "未找到目录: $SRC_DIR" >&2
  exit 1
fi

echo "准备同步:"
echo "  本地: $SRC_DIR"
echo "  远端: ${ROBOT_HOST}:${DEST_DIR}/"

ssh "$ROBOT_HOST" "mkdir -p '$DEST_DIR'"

rsync -av --delete \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'inventory/generated/runtime_*.json' \
  --exclude 'inventory/generated/runtime_*.md' \
  --exclude 'inventory/generated/phase2_*.json' \
  --exclude 'inventory/generated/phase2_*.md' \
  --exclude 'cases/*/*/runtime.json' \
  --exclude 'cases/*/*/phase2.json' \
  "$SRC_DIR" "${ROBOT_HOST}:${DEST_DIR}/"

echo "同步完成 -> ${ROBOT_HOST}:${DEST_DIR}/"
