#!/usr/bin/env python3
# backend/asr_worker.py - persistent Vosk recognizer reading base64 audio lines from stdin
# input JSON: {"data": <base64 pcm>, "robot_id": "...", "session": "...", "seq": n, "final": bool}
# output JSON: {"text": "...", "robot_id": "...", "session": "...", "seq": n, "final": bool} or {"error": "..."}

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
        rid = obj.get('robot_id', '')
        session = obj.get('session')
        seq = obj.get('seq')
        final = obj.get('final', False)
        if not b64:
            continue
        pcm = base64.b64decode(b64)
        accepted = rec.AcceptWaveform(pcm)
        if final:
            res = json.loads(rec.FinalResult())
            rec.Reset()
        else:
            if accepted:
                res = json.loads(rec.Result())
            else:
                res = json.loads(rec.PartialResult())
        text = res.get('text', '').strip()
        out = {"text": text, "robot_id": rid, "session": session, "seq": seq, "final": final}
        print(json.dumps(out), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e)}), flush=True)
