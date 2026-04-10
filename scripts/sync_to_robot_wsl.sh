#!/usr/bin/env bash
set -euo pipefail

# WSL 下同步到机器人，使用 Windows 路径时自动转换为 /mnt/ 前缀
# 用法：
#   ./scripts/sync_to_robot_wsl.sh agi@192.168.88.88:/agibot/data/home/agi/bot_connect
# 可选：
#   SRC=/mnt/h/Project/Bot/bot_connect ./scripts/sync_to_robot_wsl.sh user@host:/path

DEST="${1:-}"
if [ -z "$DEST" ]; then
  echo "用法: $0 user@host:/remote/path" >&2
  exit 1
fi

# 解析源目录
if [ -n "${SRC:-}" ]; then
  SRC_DIR="$SRC"
else
  SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
fi

# 如果是 Windows 路径，转为 /mnt/<drive> 形式
if echo "$SRC_DIR" | grep -qiE '^[A-Z]:\\'; then
  drive="$(echo "$SRC_DIR" | cut -c1 | tr 'A-Z' 'a-z')"
  rest="$(echo "$SRC_DIR" | cut -c3- | tr '\\\\' '/')"
  SRC_DIR="/mnt/$drive/$rest"
fi

if [ ! -d "$SRC_DIR" ]; then
  echo "源路径不存在: $SRC_DIR" >&2
  exit 1
fi

echo "[sync] SRC=$SRC_DIR -> DEST=$DEST"

rsync -av --delete \
  --exclude 'backend/uploads/' \
  --exclude 'frontend/node_modules/' \
  --exclude '.git/' \
  --exclude '.gitignore' \
  "$SRC_DIR"/ "$DEST"/

echo "同步完成"
