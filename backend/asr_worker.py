#!/usr/bin/env python3
# backend/asr_worker.py - 纯 Python Vosk 识别，从stdin读base64音频，stdout输出json
import sys, json, base64, os
from vosk import Model, KaldiRecognizer

MODEL_PATH = os.getenv("MODEL_PATH", r"H:\\models\\vosk-model-small-cn-0.22")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
        b64 = obj.get('data')
        if not b64:
            continue
        pcm = base64.b64decode(b64)
        if rec.AcceptWaveform(pcm):
            res = json.loads(rec.Result())
        else:
            res = json.loads(rec.FinalResult())
        text = res.get('text', '').strip()
        out = {"text": text}
        print(json.dumps(out), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e)}), flush=True)
