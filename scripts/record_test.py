"""
record_test.py
在当前机器上测试麦克风录音是否正常，并写出 wav 文件。
用法（PowerShell/CMD/WSL 均可）：
  python scripts/record_test.py --seconds 5 --out test_mic.wav
参数：
  --seconds/-s  录制时长（秒，默认 5）
  --rate/-r     采样率（默认 16000）
  --channels/-c 通道数（默认 1）
"""
import argparse
import wave
import sys

try:
    import sounddevice as sd
except Exception:
    print("缺少依赖：pip install sounddevice", file=sys.stderr)
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", "-s", type=int, default=5)
    ap.add_argument("--rate", "-r", type=int, default=16000)
    ap.add_argument("--channels", "-c", type=int, default=1)
    ap.add_argument("--out", "-o", default="test_mic.wav")
    args = ap.parse_args()

    print(f"录制 {args.seconds}s, {args.rate}Hz, {args.channels}ch -> {args.out}")
    sd.default.samplerate = args.rate
    sd.default.channels = args.channels
    audio = sd.rec(int(args.seconds * args.rate))
    sd.wait()

    # 写 WAV
    with wave.open(args.out, "wb") as wf:
        wf.setnchannels(args.channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(args.rate)
        wf.writeframes((audio * 32767).astype("int16").tobytes())
    print("完成，输出文件大小:", len(open(args.out, "rb").read()), "bytes")

if __name__ == "__main__":
    main()
