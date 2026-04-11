#!/usr/bin/env bash
set -euo pipefail

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
if [ -f "$ROS_SETUP_BASH" ]; then
  source "$ROS_SETUP_BASH"
fi
if [ -f "$AIMDK_SETUP_BASH" ]; then
  source "$AIMDK_SETUP_BASH"
fi

: "${ROBOT_ID:=${SLAVE_ROBOT_ID:-slave-01}}"
: "${STREAM_TOPIC:=/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed}"
: "${STREAM_NAME:=$ROBOT_ID}"
: "${STREAM_RTSP_PORT:=8554}"
: "${STREAM_WEBRTC_PORT:=8889}"
: "${STREAM_HLS_PORT:=8888}"
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

if ! command -v "$FFMPEG_BIN" >/dev/null 2>&1; then
  echo "[camera-stream] missing ffmpeg: $FFMPEG_BIN" >&2
  exit 1
fi
if ! command -v "$MEDIAMTX_BIN" >/dev/null 2>&1; then
  echo "[camera-stream] missing mediamtx: $MEDIAMTX_BIN" >&2
  echo "[camera-stream] install MediaMTX first, then rerun this script" >&2
  exit 1
fi

export STREAM_ENABLE=1
export STREAM_PUBLIC_HOST
export STREAM_NAME
export STREAM_TOPIC
export STREAM_RTSP_PORT
export STREAM_WEBRTC_PORT
export STREAM_HLS_PORT

export MTX_RTSPADDRESS=":${STREAM_RTSP_PORT}"
export MTX_HLSADDRESS=":${STREAM_HLS_PORT}"
export MTX_WEBRTCADDRESS=":${STREAM_WEBRTC_PORT}"
export MTX_WEBRTCADDITIONALHOSTS="${STREAM_PUBLIC_HOST}"
export MTX_WEBRTCALLOWORIGINS="*"
export MTX_HLSALLOWORIGINS="*"
export MTX_WEBRTCLOCALTCPADDRESS=":8189"

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

echo "[camera-stream] public host : ${STREAM_PUBLIC_HOST}"
echo "[camera-stream] source topic : ${STREAM_TOPIC}"
echo "[camera-stream] rtsp        : rtsp://${STREAM_PUBLIC_HOST}:${STREAM_RTSP_PORT}/${STREAM_NAME}"
echo "[camera-stream] webrtc page : http://${STREAM_PUBLIC_HOST}:${STREAM_WEBRTC_PORT}/${STREAM_NAME}"
echo "[camera-stream] whep        : http://${STREAM_PUBLIC_HOST}:${STREAM_WEBRTC_PORT}/${STREAM_NAME}/whep"
echo "[camera-stream] hls         : http://${STREAM_PUBLIC_HOST}:${STREAM_HLS_PORT}/${STREAM_NAME}/index.m3u8"

"$MEDIAMTX_BIN" &
MEDIAMTX_PID=$!
sleep 2

cd "$ROOT"
python scripts/camera_rtsp_relay.py --ros-args \
  -p topic:="${STREAM_TOPIC}" \
  -p rtsp_url:="rtsp://127.0.0.1:${STREAM_RTSP_PORT}/${STREAM_NAME}" \
  -p ffmpeg_bin:="${FFMPEG_BIN}" \
  -p qos_reliability:="${STREAM_QOS_RELIABILITY}" \
  -p qos_durability:="${STREAM_QOS_DURABILITY}" \
  -p qos_depth:="${STREAM_QOS_DEPTH}" &
RELAY_PID=$!

wait "${RELAY_PID}"
