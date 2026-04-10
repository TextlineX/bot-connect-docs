#!/usr/bin/env bash
set -euo pipefail
# 加载自定义配置，支持 CONFIG_ENV 选择 config/{ENV}.sh，默认 local
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG_ENV="${CONFIG_ENV:-local}"
CFG_PATH="$ROOT/config/${CFG_ENV}.sh"
if [ -f "$CFG_PATH" ]; then
  source "$CFG_PATH"
elif [ -f "$ROOT/config/local.sh" ]; then
  source "$ROOT/config/local.sh"
fi

: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=slave-01}"

echo "[slave] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID"
cd "$ROOT/slave"
python client.py
