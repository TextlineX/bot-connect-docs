#!/usr/bin/env bash
# 启动从机客户端（WS 客户端占位）
# 用法：
#   WS_URL=ws://192.168.31.170:8765 ROBOT_ID=slave-01 ./start_slave.sh

set -euo pipefail
cd /agibot/data/home/agi/bot_connect/slave
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=slave-01}"
export WS_URL ROBOT_ID

echo "[slave] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID"
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
python client.py
