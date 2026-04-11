#!/usr/bin/env bash
set -euo pipefail

# 多路摄像头 MJPEG 推流 + 从机客户端
# 默认端口：
#   8000 -> /aima/hal/sensor/rgb_head_rear/rgb_image/compressed
#   8001 -> /aima/hal/sensor/stereo_head_front_left/rgb_image/compressed
#   8002 -> /aima/hal/sensor/stereo_head_front_right/rgb_image/compressed
#   8003 -> /aima/hal/sensor/rgbd_head_front/rgb_image/compressed
# 可通过 STREAM_TOPICS 和 STREAM_HTTP_BASE 覆盖。

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
: "${ROBOT_ROLE:=slave}"
: "${SIM_MODE:=0}"
export WS_URL ROBOT_ID ROBOT_ROLE SIM_MODE

# 多路话题/端口
DEFAULT_TOPICS=(
  "/aima/hal/sensor/rgb_head_rear/rgb_image/compressed"
  "/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed"
  "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed"
  "/aima/hal/sensor/rgbd_head_front/rgb_image/compressed"
)

if [ -n "${STREAM_TOPICS:-}" ]; then
  IFS=',' read -r -a TOPICS <<< "${STREAM_TOPICS}"
else
  TOPICS=("${DEFAULT_TOPICS[@]}")
fi

: "${STREAM_HTTP_BASE:=8000}"

pids=()

cleanup() {
  set +e
  for pid in "${pids[@]:-}"; do
    [ -n "$pid" ] && kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

port=$STREAM_HTTP_BASE
for topic in "${TOPICS[@]}"; do
  python "$ROOT/scripts/mjpeg_http_server.py" --topic "$topic" --port "$port" &
  pids+=($!)
  echo "[stream] mjpeg=http://$(hostname -I 2>/dev/null | awk '{print $1}'):${port}/stream.mjpg (topic=$topic)"
  port=$((port + 1))
done

cd "$ROOT"
python robot/client.py
