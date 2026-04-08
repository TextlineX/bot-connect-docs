#!/usr/bin/env python3
"""
发送已知语音样例到后端，验证 audio_upload → ASR → 前端链路。
默认会下载 https://alphacephei.com/vosk/test.wav（16k单声道），
转换为 raw PCM，封装 audio_upload 发送到后端。

环境变量可覆盖：
  WS_URL   默认 ws://192.168.31.170:8765
  ROBOT_ID 默认 mock-sender
"""
import base64
import json
import os
import urllib.request
import wave
import asyncio
import websockets
from pathlib import Path

WS_URL = os.getenv("WS_URL", "ws://192.168.31.170:8765")
ROBOT_ID = os.getenv("ROBOT_ID", "mock-sender")
TEST_WAV = Path(__file__).resolve().parent / "test.wav"
TEST_URL = "https://alphacephei.com/vosk/test.wav"


def ensure_wav():
    if TEST_WAV.exists():
        return
    print("[MOCK] downloading test.wav ...")
    with urllib.request.urlopen(TEST_URL) as resp:
        TEST_WAV.write_bytes(resp.read())
    print("[MOCK] saved", TEST_WAV)


def load_raw_16k_mono(path: Path):
    with wave.open(str(path), 'rb') as wf:
        rate = wf.getframerate()
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    if rate != 16000 or channels != 1 or sampwidth != 2:
        raise SystemExit(f"test.wav 必须是16k/单声道/16bit，当前 rate={rate}, ch={channels}, width={sampwidth}")
    return frames

async def main():
    ensure_wav()
    pcm = load_raw_16k_mono(TEST_WAV)
    b64 = base64.b64encode(pcm).decode()
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type":"hello","robot_id":ROBOT_ID,"ts":0}))
        msg = {
            "type": "audio_upload",
            "robot_id": ROBOT_ID,
            "payload": {"mime": "audio/raw;rate=16000;channels=1;format=S16_LE", "data": b64},
            "ts": 0
        }
        await ws.send(json.dumps(msg))
        print("[MOCK] sent test.wav as audio_upload, bytes=", len(pcm))
        # 等待服务器回执/转发几条消息后退出
        try:
            for _ in range(5):
                raw = await asyncio.wait_for(ws.recv(), timeout=2)
                print("[MOCK] recv:", raw)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
