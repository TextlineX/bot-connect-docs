#!/usr/bin/env bash
set -euo pipefail
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=master-01}"
: "${TTS_SERVICE:=/aimdk_5Fmsgs/srv/PlayTts}"

echo "[master] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID TTS_SERVICE=$TTS_SERVICE"
cd /mnt/h/Project/Bot/bot_connect/master
python client.py
