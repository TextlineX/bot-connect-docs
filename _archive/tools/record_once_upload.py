#!/usr/bin/env python3
"""
录制一次音频并通过 WebSocket 以 audio_upload 发送（方便手动排查录音问题）。
环境变量：
  WS_URL      默认 ws://192.168.31.170:8765
  ROBOT_ID    默认 manual-recorder
  DURATION    录制时长秒，默认 3
  DEVICE      arecord 设备，如 plughw:0,0；留空用默认设备
要求：机器人已安装 alsa-utils，WS 后端在运行。
"""
import os, json, time, base64, subprocess, asyncio, websockets

WS_URL = os.getenv('WS_URL', 'ws://192.168.31.170:8765')
ROBOT_ID = os.getenv('ROBOT_ID', 'manual-recorder')
DURATION = int(os.getenv('DURATION', '3'))
DEVICE = os.getenv('DEVICE', '')

async def record_and_send():
    cmd = ['arecord', '-f', 'S16_LE', '-c1', '-r', '16000', '-d', str(DURATION), '-t', 'raw']
    if DEVICE:
        cmd[1:1] = ['-D', DEVICE]
    print('>',' '.join(cmd))
    pcm = subprocess.check_output(cmd)
    b64 = base64.b64encode(pcm).decode()
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type":"hello","robot_id":ROBOT_ID,"ts":time.time()}))
        msg = {
            "type": "audio_upload",
            "robot_id": ROBOT_ID,
            "payload": {"mime": "audio/raw;rate=16000;channels=1;format=S16_LE", "data": b64},
            "ts": time.time()
        }
        await ws.send(json.dumps(msg))
        print(f"sent {len(pcm)} bytes")
        try:
            for _ in range(3):
                raw = await asyncio.wait_for(ws.recv(), timeout=2)
                print('recv', raw)
        except Exception:
            pass

if __name__ == '__main__':
    asyncio.run(record_and_send())
