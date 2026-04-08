import base64
import asyncio
import os
import subprocess
import tempfile

# 可选依赖：vosk。本机主机需提前 pip 安装 vosk 并准备 MODEL_PATH
try:
    from vosk import Model, KaldiRecognizer
except Exception:
    Model = None
    KaldiRecognizer = None

model_path = os.getenv("MODEL_PATH")
_model = None


def _load_model():
    global _model
    if _model or not Model or not model_path:
        return _model
    try:
        _model = Model(model_path)
    except Exception:
        _model = None
    return _model


def _to_pcm16(raw: bytes, mime: str) -> bytes:
    """将 webm/ogg 等压缩音频转 16k mono s16le；若已是 raw 则直接返回"""
    mime = mime or ""
    if mime.startswith("audio/raw") or mime.startswith("audio/pcm"):
        return raw
    # 需要 ffmpeg 支持
    with tempfile.NamedTemporaryFile(suffix=".bin") as inp, tempfile.NamedTemporaryFile(suffix=".raw") as outp:
        inp.write(raw)
        inp.flush()
        cmd = [
            "ffmpeg", "-y",
            "-i", inp.name,
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            outp.name
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return outp.read()
        except Exception:
            return b""


async def handle_audio_upload(data: dict) -> str:
    """接收 WS audio_upload，返回识别文本；若未配置 MODEL_PATH 或无 vosk，则返回空字符串"""
    try:
        payload = data.get("payload", {})
        b64 = payload.get("data", "")
        mime = payload.get("mime", "")
        raw = base64.b64decode(b64) if b64 else b""
    except Exception:
        return ""

    if not raw or not _load_model() or not KaldiRecognizer:
        return ""

    pcm = _to_pcm16(raw, mime)
    if not pcm:
        return ""

    rec = KaldiRecognizer(_model, 16000)
    rec.AcceptWaveform(pcm)
    res = rec.Result()
    try:
        import json
        text = json.loads(res).get("text", "")
    except Exception:
        text = ""
    return text
