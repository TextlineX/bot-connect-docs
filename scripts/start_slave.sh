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

# 连接配置
: "${WS_URL:=ws://127.0.0.1:8765}"
: "${SLAVE_ROBOT_ID:=}"
if [ -n "${SLAVE_ROBOT_ID}" ]; then
  ROBOT_ID="${SLAVE_ROBOT_ID}"
else
  ROBOT_ID="slave-01"
fi
export ROBOT_ROLE="slave"

# 视频流（默认开启，缺依赖会自动跳过）
STREAM_ENABLE=${STREAM_ENABLE:-1}
: "${STREAM_MODE:=rtsp}"   # rtsp | http_mjpeg
: "${STREAM_TOPIC:=/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed}"
: "${STREAM_NAME:=$ROBOT_ID}"
: "${STREAM_RTSP_PORT:=8554}"
: "${STREAM_WEBRTC_PORT:=8889}"
: "${STREAM_HLS_PORT:=8888}"
: "${STREAM_HTTP_PORT:=8000}"
: "${FFMPEG_BIN:=ffmpeg}"
: "${MEDIAMTX_BIN:=mediamtx}"

if [ -z "${STREAM_QOS_RELIABILITY:-}" ]; then
  if [[ "$STREAM_TOPIC" == *"/rgbd_head_front/"* ]]; then
    STREAM_QOS_RELIABILITY="reliable"
  else
    STREAM_QOS_RELIABILITY="best_effort"
  fi
fi
: "${STREAM_QOS_DURABILITY:=volatile}"
: "${STREAM_QOS_DEPTH:=5}"

if [ -z "${STREAM_PUBLIC_HOST:-}" ]; then
  STREAM_PUBLIC_HOST="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi
if [ -z "${STREAM_PUBLIC_HOST:-}" ]; then
  STREAM_PUBLIC_HOST="$(hostname)"
fi

start_stream() {
  if [ "$STREAM_ENABLE" != "1" ]; then
    echo "[stream] 跳过，STREAM_ENABLE=$STREAM_ENABLE"
    return
  fi
  if ! command -v "$FFMPEG_BIN" >/dev/null 2>&1; then
    echo "[stream] 缺少 ffmpeg ($FFMPEG_BIN)，关闭推流"
    return
  fi
  if ! command -v "$MEDIAMTX_BIN" >/dev/null 2>&1; then
    echo "[stream] 缺少 mediamtx ($MEDIAMTX_BIN)，关闭推流"
    return
  fi

  export MTX_RTSPADDRESS=":${STREAM_RTSP_PORT}"
  export MTX_HLSADDRESS=":${STREAM_HLS_PORT}"
  export MTX_WEBRTCADDRESS=":${STREAM_WEBRTC_PORT}"
  export MTX_WEBRTCADDITIONALHOSTS="${STREAM_PUBLIC_HOST}"
  export MTX_WEBRTCALLOWORIGINS="*"
  export MTX_HLSALLOWORIGINS="*"
  export MTX_WEBRTCLOCALTCPADDRESS=":8189"

  echo "[stream] public host : ${STREAM_PUBLIC_HOST}"
  echo "[stream] source topic: ${STREAM_TOPIC}"
  echo "[stream] rtsp        : rtsp://${STREAM_PUBLIC_HOST}:${STREAM_RTSP_PORT}/${STREAM_NAME}"
  echo "[stream] webrtc page : http://${STREAM_PUBLIC_HOST}:${STREAM_WEBRTC_PORT}/${STREAM_NAME}"
  echo "[stream] whep        : http://${STREAM_PUBLIC_HOST}:${STREAM_WEBRTC_PORT}/${STREAM_NAME}/whep"
  echo "[stream] hls         : http://${STREAM_PUBLIC_HOST}:${STREAM_HLS_PORT}/${STREAM_NAME}/index.m3u8"

  "$MEDIAMTX_BIN" >/tmp/mediamtx.log 2>&1 &
  MEDIAMTX_PID=$!
  sleep 2

  python "$ROOT/scripts/camera_rtsp_relay.py" --ros-args \
    -p topic:="${STREAM_TOPIC}" \
    -p rtsp_url:="rtsp://127.0.0.1:${STREAM_RTSP_PORT}/${STREAM_NAME}" \
    -p ffmpeg_bin:="${FFMPEG_BIN}" \
    -p input_format:="${STREAM_INPUT_FORMAT:-mjpeg}" \
    -p qos_reliability:="${STREAM_QOS_RELIABILITY}" \
    -p qos_durability:="${STREAM_QOS_DURABILITY}" \
    -p qos_depth:="${STREAM_QOS_DEPTH}" &
  RELAY_PID=$!
}

cleanup() {
  set +e
  if [ -n "${RELAY_PID:-}" ] && kill -0 "${RELAY_PID}" 2>/dev/null; then
    kill "${RELAY_PID}" 2>/dev/null || true
    wait "${RELAY_PID}" 2>/dev/null || true
  fi
  if [ -n "${MEDIAMTX_PID:-}" ] && kill -0 "${MEDIAMTX_PID}" 2>/dev/null; then
    kill "${MEDIAMTX_PID}" 2>/dev/null || true
    wait "${MEDIAMTX_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "[slave] WS_URL=$WS_URL ROBOT_ID=$ROBOT_ID"
start_stream

cd "$ROOT"
python robot/client.py
