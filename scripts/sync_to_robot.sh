#!/usr/bin/env bash
set -euo pipefail

# 将本机仓库同步到机器人（覆盖式），忽略 uploads/ 测试音频等
# 用法：
#   ./scripts/sync_to_robot.sh robot_user@robot_ip:/agibot/data/home/agi/bot_connect
#
# 依赖：rsync

if [ $# -lt 1 ]; then
  echo "用法: $0 user@host:/remote/path" >&2
  exit 1
fi

DEST="$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rsync -av --delete \
  --exclude 'backend/uploads/' \
  --exclude 'frontend/node_modules/' \
  --exclude '.git/' \
  --exclude '.gitignore' \
  "$ROOT/" "$DEST/"

echo "同步完成 -> $DEST"
