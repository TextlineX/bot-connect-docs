#!/usr/bin/env python3
import os, json, base64, asyncio, websockets
from vosk import Model, KaldiRecognizer

WS_URL = os.getenv("WS_URL", "ws://192.168.31.170:8765")
MODEL_PATH = os.getenv("MODEL_PATH", r"H:\\models\\vosk-model-small-cn-0.22")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)

async def main():
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                await ws.send(json.dumps({"type":"hello","robot_id":"asr-bridge","ts":0}))
                print("[ASR] connected to", WS_URL)
                async for raw in ws:
                    try:
                        data = json.loads(raw)
                    except Exception:
                        continue
                    if data.get("type") != "audio_upload":
                        continue
                    b64 = (data.get("payload") or {}).get("data")
                    if not b64:
                        continue
                    pcm = base64.b64decode(b64)
                    if rec.AcceptWaveform(pcm):
                        res = json.loads(rec.Result())
                    else:
                        res = json.loads(rec.FinalResult())
                    text = res.get("text","" ).strip()
                    if text:
                        print("[ASR]", text)
                        await ws.send(json.dumps({
                            "type": "asr_text",
                            "robot_id": "asr-bridge",
                            "text": text,
                            "ts": 0
                        }))
        except Exception as e:
            print("[ASR] reconnect in 3s:", e)
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
