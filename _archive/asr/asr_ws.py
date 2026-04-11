#!/usr/bin/env python3
"""
ASR -> TTS 回声 + 可选推送到 WebSocket 后端（前端显示 asr_text）
环境变量新增：
  WS_URL      默认空；如设为 ws://<PC_IP>:8765 则推送 asr_text
  WS_ROBOT_ID 默认 asr-bridge
"""
import os
import json
import roslibpy
import websockets
import asyncio
from vosk import Model, KaldiRecognizer

ROSBRIDGE_IP = os.getenv('ROSBRIDGE_IP', '192.168.1.1')
ROSBRIDGE_PORT = int(os.getenv('ROSBRIDGE_PORT', '9090'))
MODEL_PATH = os.getenv('MODEL_PATH', '')
AUDIO_TOPIC = os.getenv('AUDIO_TOPIC', '/aima/hal/audio/capture')
SR = int(os.getenv('SR', '16000'))
ENABLE_TTS = os.getenv('ENABLE_TTS', '0') == '1'
TTS_SERVICE = os.getenv('TTS_SERVICE', '/aimdk_5Fmsgs/srv/PlayTts')
WS_URL = os.getenv('WS_URL', '')
WS_ROBOT_ID = os.getenv('WS_ROBOT_ID', 'asr-bridge')

if not MODEL_PATH:
    raise SystemExit('请设置 MODEL_PATH 指向 Vosk 模型目录')

print(f"[ASR] rosbridge ws://{ROSBRIDGE_IP}:{ROSBRIDGE_PORT}")
print(f"[ASR] model: {MODEL_PATH}")
print(f"[ASR] audio topic: {AUDIO_TOPIC}, sr={SR}, TTS={ENABLE_TTS}")
if WS_URL:
    print(f"[ASR] push asr_text -> {WS_URL}")

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SR)

client = roslibpy.Ros(host=ROSBRIDGE_IP, port=ROSBRIDGE_PORT)
client.run()

pub_text = roslibpy.Topic(client, '/asr/text', 'std_msgs/String')
sub_audio = roslibpy.Topic(client, AUDIO_TOPIC, 'aimdk_msgs/msg/AudioCapture')

# ---------- 可选 WebSocket 推送 ----------
ws_conn = None
async def ws_loop():
    global ws_conn
    if not WS_URL:
        return
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                ws_conn = ws
                hello = { 'type': 'hello', 'robot_id': WS_ROBOT_ID, 'ts': 0 }
                await ws.send(json.dumps(hello))
                await asyncio.Future()  # 保持连接
        except Exception as e:
            print('[ASR][WS] reconnect in 3s', e)
            await asyncio.sleep(3)

asyncio.get_event_loop().create_task(ws_loop())

async def push_ws_text(text: str):
    if ws_conn and WS_URL:
        try:
            msg = { 'type': 'asr_text', 'text': text, 'robot_id': WS_ROBOT_ID, 'ts': 0 }
            await ws_conn.send(json.dumps(msg))
        except Exception as e:
            print('[ASR][WS] send err', e)

# ---------- TTS 调用 ----------

def call_tts(text: str):
    service = roslibpy.Service(client, TTS_SERVICE, 'aimdk_msgs/srv/PlayTts')
    req = roslibpy.ServiceRequest({
        'tts_req': {
            'text': text,
            'domain': 'asr_echo',
            'trace_id': 'asr',
            'is_interrupted': True,
            'priority_weight': 0,
            'priority_level': { 'value': 6 }
        }
    })
    try:
        resp = service.call(req, timeout=8.0)
        ok = bool(resp.get('tts_resp', {}).get('is_success', False))
        print('[TTS]', 'ok' if ok else 'failed', text)
    except Exception as e:
        print('[TTS] error', e)

# ---------- 音频回调 ----------

def pcm_from(msg: dict) -> bytes:
    for k in ('data', 'pcm', 'audio'):
        if k in msg:
            try:
                return roslibpy.Message.to_binary(msg[k])
            except Exception:
                pass
    return b''

def on_audio(msg):
    pcm = pcm_from(msg)
    if not pcm:
        return
    if rec.AcceptWaveform(pcm):
        res = json.loads(rec.Result())
    else:
        res = json.loads(rec.PartialResult())
    text = res.get('text', '').strip()
    if text:
        pub_text.publish({ 'data': text })
        print('[ASR]', text)
        if ENABLE_TTS:
            call_tts(text)
        if WS_URL:
            asyncio.get_event_loop().create_task(push_ws_text(text))

sub_audio.subscribe(on_audio)
print('[ASR] started, press Ctrl+C to exit')
client.run_forever()
PY
