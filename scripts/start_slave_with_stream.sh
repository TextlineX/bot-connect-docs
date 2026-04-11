#!/usr/bin/env bash
set -euo pipefail

# 配置加载（复用 config/{env}.sh）
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG_ENV="${CONFIG_ENV:-local}"
CFG_PATH="$ROOT/config/${CFG_ENV}.sh"
if [ -f "$CFG_PATH" ]; then
  source "$CFG_PATH"
elif [ -f "$ROOT/config/local.sh" ]; then
  source "$ROOT/config/local.sh"
fi

: "${ROS_SETUP_BASH:=/opt/ros/humble/setup.bash}"
: "${AIMDK_SETUP_BASH:=/agibot/data/home/agi/aimdk/install/setup.bash}"
safe_source() {
  local f="$1"
  [ -f "$f" ] || return 0
  set +u   # ROS setup 会访问未定义变量，临时关闭 -u
  source "$f"
  set -u
}
safe_source "$ROS_SETUP_BASH"
safe_source "$AIMDK_SETUP_BASH"

# 基础环境
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${ROBOT_ID:=slave-01}"
: "${ROBOT_ROLE:=slave}"
: "${SIM_MODE:=0}"
export WS_URL ROBOT_ID ROBOT_ROLE SIM_MODE

# 推流参数
: "${STREAM_PUBLIC_HOST:=$(hostname -I 2>/dev/null | awk '{print $1}')}"
: "${STREAM_NAME:=$ROBOT_ID}"
: "${STREAM_TOPIC:=/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed}"
: "${STREAM_RTSP_PORT:=8554}"
: "${STREAM_WEBRTC_PORT:=8889}"
: "${STREAM_HLS_PORT:=8888}"
: "${STREAM_QOS_RELIABILITY:=best_effort}"
: "${STREAM_QOS_DURABILITY:=volatile}"
: "${STREAM_QOS_DEPTH:=5}"
: "${STREAM_INPUT_FORMAT:=mjpeg}"   # mjpeg | h264
: "${STREAM_MODE:=rtsp}"            # rtsp | http_mjpeg
: "${STREAM_HTTP_PORT:=8000}"

MEDIAMTX_BIN=${MEDIAMTX_BIN:-mediamtx}
FFMPEG_BIN=${FFMPEG_BIN:-ffmpeg}

start_mediamtx() {
  if pgrep -x mediamtx >/dev/null 2>&1; then
    return
  fi
  export MTX_RTSPADDRESS=":${STREAM_RTSP_PORT}"
  export MTX_HLSADDRESS=":${STREAM_HLS_PORT}"
  export MTX_WEBRTCADDRESS=":${STREAM_WEBRTC_PORT}"
  export MTX_WEBRTCADDITIONALHOSTS="${STREAM_PUBLIC_HOST}"
  export MTX_WEBRTCALLOWORIGINS="*"
  export MTX_HLSALLOWORIGINS="*"
  export MTX_WEBRTCLOCALTCPADDRESS=":8189"
  "$MEDIAMTX_BIN" >/tmp/mediamtx.log 2>&1 &
  sleep 1
}

start_relay() {
  python "$ROOT/scripts/camera_rtsp_relay.py" --ros-args \
    -p topic:="$STREAM_TOPIC" \
    -p rtsp_url:="rtsp://127.0.0.1:${STREAM_RTSP_PORT}/${STREAM_NAME}" \
    -p ffmpeg_bin:="$FFMPEG_BIN" \
    -p input_format:="${STREAM_INPUT_FORMAT:-mjpeg}" \
    -p qos_reliability:="$STREAM_QOS_RELIABILITY" \
    -p qos_durability:="$STREAM_QOS_DURABILITY" \
    -p qos_depth:="$STREAM_QOS_DEPTH" &
  RELAY_PID=$!
}

cleanup() {
  set +e
  [ -n "${RELAY_PID:-}" ] && kill "$RELAY_PID" 2>/dev/null || true
  [ -n "${MJPEG_PID:-}" ] && kill "$MJPEG_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [ "$STREAM_MODE" = "http_mjpeg" ]; then
  python "$ROOT/scripts/mjpeg_http_server.py" --topic "$STREAM_TOPIC" --port "$STREAM_HTTP_PORT" &
  MJPEG_PID=$!
  echo "[stream] mjpeg=http://${STREAM_PUBLIC_HOST}:${STREAM_HTTP_PORT}/stream.mjpg (topic=$STREAM_TOPIC)"
else
  start_mediamtx
  start_relay
  echo "[stream] rtsp=rtsp://${STREAM_PUBLIC_HOST}:${STREAM_RTSP_PORT}/${STREAM_NAME}"
  echo "[stream] whep=http://${STREAM_PUBLIC_HOST}:${STREAM_WEBRTC_PORT}/${STREAM_NAME}/whep"
fi

cd "$ROOT"
python robot/client.py
