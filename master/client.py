# 主机示例：把收到的 cmd_vel / tts 映射到 SDK，占位运动+真实 TTS 服务
import os
import time
import sys
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
if COMMON.as_posix() not in sys.path:
    sys.path.insert(0, COMMON.as_posix())

from ws_client import WsClient
from tts_client import send_tts, shutdown as tts_shutdown

WS_URL = os.getenv('WS_URL', 'ws://127.0.0.1:8765')
ROBOT_ID = os.getenv('ROBOT_ID', 'master-01')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

# 占位运动接口（需要时换成真实 SDK）
class RobotSDK:
    def set_velocity(self, linear: float, angular: float):
        print(f"[MASTER SDK] set_velocity linear={linear} angular={angular}")

    def status(self):
        return {'ts': time.time()}

sdk = RobotSDK()


def on_cmd(data):
    p = data.get('payload', {})
    sdk.set_velocity(p.get('linear', 0), p.get('angular', 0))


def on_exec(data):
    payload = data.get('payload', {})
    if payload.get('action') == 'tts':
        text = payload.get('text', '') or '你好，我是灵犀。'
        send_tts(text)


def status_provider():
    return {'role': 'master', **sdk.status()}


def main():
    client = WsClient(ROBOT_ID, WS_URL, AUTH_TOKEN,
                      on_cmd=on_cmd, on_exec=on_exec,
                      status_provider=status_provider)
    try:
        asyncio.run(client.run())
    finally:
        tts_shutdown()


if __name__ == '__main__':
    main()
