"""
Simple ASR handler for master: decode base64 PCM, feed Vosk, return text.
Env:
  MODEL_PATH: path to Vosk model (default H:\\models\\vosk-model-small-cn-0.22)
Assumes audio is 16k mono s16le (backend已转码).
"""
import base64
import os
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = os.getenv("MODEL_PATH", r"H:\\models\\vosk-model-small-cn-0.22")
_model = Model(MODEL_PATH)
_rec = KaldiRecognizer(_model, 16000)


def _is_raw_pcm(mime: str | None) -> bool:
    if not mime:
        return False
    m = mime.lower()
    return m.startswith("audio/raw") or m.startswith("audio/pcm") or "s16_le" in m or "s16le" in m


def handle_audio_upload(data: dict) -> str:
    """
    data: {"type":"audio_upload","payload":{"data":b64,"mime":...,"final":bool,...}}
    returns ASR text (str), or "" if no text/unsupported mime.
    """
    try:
        payload = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        b64 = payload.get("data")
        mime = payload.get("mime", "")
        final = payload.get("final", False)
        if not b64 or not _is_raw_pcm(mime):
            return ""
        pcm = base64.b64decode(b64)
        accepted = _rec.AcceptWaveform(pcm)
        if final:
            res = json.loads(_rec.FinalResult())
            _rec.Reset()
        else:
            res = json.loads(_rec.Result()) if accepted else json.loads(_rec.PartialResult())
        text = (res.get("text") or res.get("partial") or "").strip()
        if text:
            print(f"[master asr] {text}")
        return text
    except Exception:
        return ""
