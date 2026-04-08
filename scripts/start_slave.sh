#!/usr/bin/env bash
set -euo pipefail
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=slave-01}"

echo "[slave] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID"
cd /mnt/h/Project/Bot/bot_connect/slave
python client.py
