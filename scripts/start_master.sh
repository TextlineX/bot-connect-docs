#!/usr/bin/env bash
# 启动主机客户端（WS 客户端 + TTS）
# 用法：
#   WS_URL=ws://192.168.31.170:8765 ROBOT_ID=master-01 TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts ./start_master.sh

set -euo pipefail
cd /agibot/data/home/agi/bot_connect/master
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=master-01}"
: "${TTS_SERVICE:=/aimdk_5Fmsgs/srv/PlayTts}"
export WS_URL ROBOT_ID TTS_SERVICE

echo "[master] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID TTS_SERVICE=$TTS_SERVICE"
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
python client.py
