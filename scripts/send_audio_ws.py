"""
用 Python 直接把本地音频文件通过 WS 发给后端，便于排查“上传后变成几 KB”问题。
用法：
  set WS_URL=ws://192.168.31.170:8765
  set ROBOT_ID=controller
  python scripts/send_audio_ws.py path\\to\\file.wav
"""
import asyncio, websockets, json, base64, sys, os

WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")
ROBOT_ID = os.getenv("ROBOT_ID", "controller")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python send_audio_ws.py <audio_file>")
        return
    path = sys.argv[1]
    buf = open(path, "rb").read()
    lower = path.lower()
    if lower.endswith(".raw") or lower.endswith(".pcm"):
        mime = "audio/pcm;rate=16000;channels=1;format=S16_LE"
    elif lower.endswith(".mp3"):
        mime = "audio/mpeg"
    elif lower.endswith(".ogg"):
        mime = "audio/ogg"
    elif lower.endswith(".webm"):
        mime = "audio/webm"
    else:
        mime = "audio/wav"
    b64 = base64.b64encode(buf).decode()
    print(f"file={path}, size={len(buf)} bytes, mime={mime}")
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type":"hello","robot_id":ROBOT_ID}))
        print(await ws.recv())  # ack
        await ws.send(json.dumps({
            "type":"audio_upload",
            "robot_id":ROBOT_ID,
            "payload":{
                "mime":mime,
                "data":b64,
                "session":"manual",
                "seq":1,
                "final":True
            },
            "ts":0
        }))
        # 等待后端确认或 asr_text
        try:
            for _ in range(3):
                msg = await asyncio.wait_for(ws.recv(), timeout=3)
                print("recv:", msg)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
