#!/usr/bin/env python3
"""
ASR -> TTS 回声脚本（运行在 PC，连接机器人 rosbridge）
- 订阅 /aima/hal/audio/capture (aimdk_msgs/msg/AudioCapture)，提取 PCM
- Vosk 识别文本，发布到 /asr/text (std_msgs/String)
- 可选：将识别文本调用 PlayTts 服务播报（设置 ENABLE_TTS=1）

环境变量：
  ROSBRIDGE_IP   默认 192.168.1.1
  ROSBRIDGE_PORT 默认 9090
  MODEL_PATH     必填，指向 Vosk 模型目录（含 conf/model files）
  AUDIO_TOPIC    默认 /aima/hal/audio/capture
  SR             默认 16000 (采样率)
  ENABLE_TTS     默认 0；设为 1 则调用 PlayTts 服务回声
  TTS_SERVICE    默认 /aimdk_5Fmsgs/srv/PlayTts

依赖安装（PC）：
  pip install -r asr/requirements.txt
模型示例：
  mkdir -p ~/models && cd ~/models
  # 下载并解压 vosk-model-small-cn-0.22.zip -> ~/models/vosk

运行：
  python asr/asr_ws.py
"""
import os
import json
import roslibpy
from vosk import Model, KaldiRecognizer

ROSBRIDGE_IP = os.getenv('ROSBRIDGE_IP', '192.168.1.1')
ROSBRIDGE_PORT = int(os.getenv('ROSBRIDGE_PORT', '9090'))
MODEL_PATH = os.getenv('MODEL_PATH', '')
AUDIO_TOPIC = os.getenv('AUDIO_TOPIC', '/aima/hal/audio/capture')
SR = int(os.getenv('SR', '16000'))
ENABLE_TTS = os.getenv('ENABLE_TTS', '0') == '1'
TTS_SERVICE = os.getenv('TTS_SERVICE', '/aimdk_5Fmsgs/srv/PlayTts')

if not MODEL_PATH:
    raise SystemExit('请设置 MODEL_PATH 指向 Vosk 模型目录')

print(f"[ASR] connect rosbridge ws://{ROSBRIDGE_IP}:{ROSBRIDGE_PORT}")
print(f"[ASR] model: {MODEL_PATH}")
print(f"[ASR] audio topic: {AUDIO_TOPIC}, sr={SR}, TTS={ENABLE_TTS}")

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SR)

client = roslibpy.Ros(host=ROSBRIDGE_IP, port=ROSBRIDGE_PORT)
client.run()

pub_text = roslibpy.Topic(client, '/asr/text', 'std_msgs/String')
sub_audio = roslibpy.Topic(client, AUDIO_TOPIC, 'aimdk_msgs/msg/AudioCapture')

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

sub_audio.subscribe(on_audio)
print('[ASR] started, press Ctrl+C to exit')
client.run_forever()
PY
