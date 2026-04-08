r"""
脚本：离线测试 Vosk 识别效果，便于排查“<empty>”问题。
用法示例：
  PowerShell:  $env:MODEL_PATH="H:\models\vosk-model-small-cn-0.22"
               python scripts\test_asr_file.py backend\uploads\1775662004259_controller.raw --mime audio/pcm
  CMD:         set MODEL_PATH=H:\models\vosk-model-small-cn-0.22
               python scripts\\test_asr_file.py backend\\uploads\\example.webm

参数:
  file          要测试的音频文件，支持 wav/mp3/webm/ogg/raw/pcm
  --mime        可选，若是原始 PCM/RAW 需注明格式，例：audio/pcm;rate=16000;channels=1;format=S16_LE
  --ffmpeg      可选，指定 ffmpeg 可执行路径，默认使用环境中的 ffmpeg

输出:
  - 解码后的 PCM 时长（秒）
  - Vosk 返回的识别文本
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile

try:
    from vosk import Model, KaldiRecognizer
except Exception as e:
    print("未安装 vosk：pip install vosk", file=sys.stderr)
    sys.exit(1)


def load_model():
    model_path = os.getenv("MODEL_PATH")
    if not model_path:
        print("环境变量 MODEL_PATH 未设置", file=sys.stderr)
        sys.exit(1)
    return Model(model_path)


def transcode_to_pcm(path, mime, ffmpeg_bin):
    # 已经是裸 PCM
    if mime and mime.lower().startswith(("audio/raw", "audio/pcm")):
        with open(path, "rb") as f:
            buf = f.read()
        return buf
    # 其他压缩格式，走 ffmpeg
    with open(path, "rb") as f:
        data = f.read()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        "pipe:0",
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "pipe:1",
    ]
    r = subprocess.run(cmd, input=data, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        print("ffmpeg 转码失败", file=sys.stderr)
        sys.exit(1)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="待识别音频文件")
    ap.add_argument("--mime", default="", help="输入 MIME，原始 PCM/RAW 必填")
    ap.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg 可执行路径")
    args = ap.parse_args()

    model = load_model()
    pcm = transcode_to_pcm(args.file, args.mime, args.ffmpeg)
    dur = len(pcm) / 2 / 16000
    print(f"解码后 PCM 长度: {len(pcm)} bytes, 时长约 {dur:.2f} 秒")

    rec = KaldiRecognizer(model, 16000)
    rec.AcceptWaveform(pcm)
    res = json.loads(rec.FinalResult())
    print("识别结果:", res.get("text", ""))


if __name__ == "__main__":
    main()
