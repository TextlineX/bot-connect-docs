#!/usr/bin/env python3
# backend/asr_worker.py - persistent Vosk recognizer reading base64 audio lines from stdin
# input JSON: {"data": <base64 pcm>, "robot_id": "...", "session": "...", "seq": n, "final": bool}
# output JSON: {"text": "...", "robot_id": "...", "session": "...", "seq": n, "final": bool} or {"error": "..."}

import sys, json, base64, os, re
from pathlib import Path
from vosk import Model, KaldiRecognizer


def normalize_model_path(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return raw
    if os.name != "nt":
        match = re.match(r"^([A-Za-z]):[\\/](.*)$", raw)
        if match:
            drive = match.group(1).lower()
            rest = match.group(2).replace("\\", "/")
            return f"/mnt/{drive}/{rest}"
    return raw


def resolve_model_path() -> str:
    root = Path(__file__).resolve().parents[1]
    candidates = []
    env_path = normalize_model_path(os.getenv("MODEL_PATH", ""))
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend([
        Path(normalize_model_path(r"H:\models\vosk-model-small-cn-0.22")),
        Path("/mnt/h/models/vosk-model-small-cn-0.22"),
        root / "models" / "vosk-model-small-cn-0.22",
    ])
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    searched = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"未找到 Vosk 模型目录，请设置 MODEL_PATH。已尝试: {searched}")


MODEL_PATH = resolve_model_path()
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
        text = (res.get('text') or res.get('partial') or '').strip()
        out = {"text": text, "robot_id": rid, "session": session, "seq": seq, "final": final}
        print(json.dumps(out), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e)}), flush=True)
