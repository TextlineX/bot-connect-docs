#!/usr/bin/env python3
# 主机客户端：自动检测 ROS/TTS；不可用则退化为模拟模式
import os
import time
import sys
import asyncio
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
HANDLERS = ROOT / "master" / "handlers"
for p in (COMMON, HANDLERS):
  if p.as_posix() not in sys.path:
    sys.path.insert(0, p.as_posix())

from ws_client import WsClient

SIM_MODE = os.getenv("SIM_MODE", "0") == "1"
send_tts = None
tts_shutdown = None

if not SIM_MODE:
  try:
    from tts_client import send_tts, shutdown as tts_shutdown  # type: ignore
    print("[master] ROS/TTS 模式")
  except Exception as e:
    print(f"[master] ROS/TTS 不可用，切换模拟模式: {e}")
    SIM_MODE = True

if SIM_MODE:
  print("[master] SIM 模式（仅 WS，不调用 ROS/TTS）")

  def send_tts(text: str):
    print(f"[SIM TTS] {text}")
    return True

  def tts_shutdown():
    pass

WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")
ROBOT_ID = os.getenv("ROBOT_ID", "master-01")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TTS_SERVICE = os.getenv("TTS_SERVICE", "/aimdk_5Fmsgs/srv/PlayTts")
AUDIO_TOPIC = os.getenv("AUDIO_TOPIC", "/aima/hal/audio/capture")


class RobotSDK:
  def set_velocity(self, linear: float, angular: float):
    print(f"[MASTER SDK] set_velocity linear={linear} angular={angular}")

  def status(self):
    return {"ts": time.time()}


sdk = RobotSDK()


async def on_exec(ws, data):
  payload = data.get("payload", {})
  if payload.get("action") == "tts":
    text = payload.get("text", "") or "你好，我是灵犀。"
    send_tts(text)


async def capability_loop(ws):
  """定期上报可用能力（TTS 服务 / 音频话题），便于前端自动启用功能。"""
  while True:
    caps = {
      "type": "capabilities",
      "robot_id": ROBOT_ID,
      "ts": time.time(),
      "payload": {
        "sim_mode": SIM_MODE,
        "tts": {
          "available": not SIM_MODE,
          "service": TTS_SERVICE,
        },
        "topics": {
          "audio_capture": AUDIO_TOPIC,
        },
      },
    }
    try:
      await ws.send(json.dumps(caps))
    except Exception as e:
      print("capabilities send error", e)
    await asyncio.sleep(10)


def on_cmd(data):
  p = data.get("payload", {})
  sdk.set_velocity(p.get("linear", 0), p.get("angular", 0))


def status_provider():
  return {"role": "master", **sdk.status()}


async def main_async():
  client = WsClient(
    ROBOT_ID,
    WS_URL,
    AUTH_TOKEN,
    on_cmd=on_cmd,
    status_provider=status_provider,
    on_open=capability_loop,
  )
  orig_handle = client.handle_message

  try:
    from audio_upload_handler import handle_audio_upload
  except Exception:
    handle_audio_upload = None

  async def wrapped_handle(ws, data):
    if data.get("type") == "exec":
      await on_exec(ws, data)
    elif data.get("type") == "audio_upload" and handle_audio_upload:
      text = await handle_audio_upload(data)
      reply = {
        "type": "asr_text",
        "robot_id": ROBOT_ID,
        "ts": time.time(),
        "text": text or "",
        "detail": "from master/audio_upload",
      }
      try:
        await ws.send(json.dumps(reply))
      except Exception:
        pass
    else:
      await orig_handle(ws, data)

  client.handle_message = wrapped_handle
  try:
    await client.run()
  finally:
    tts_shutdown()


def main():
  asyncio.run(main_async())


if __name__ == "__main__":
  main()
