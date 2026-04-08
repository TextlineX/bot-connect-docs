# 从机示例：同样监听 cmd_vel，可在 on_exec 加自定义动作
import os
import time
import sys
from pathlib import Path

# 确保可以找到上级 common 目录
ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
if COMMON.as_posix() not in sys.path:
    sys.path.insert(0, COMMON.as_posix())

from ws_client import WsClient

WS_URL = os.getenv('WS_URL', 'ws://127.0.0.1:8765')
ROBOT_ID = os.getenv('ROBOT_ID', 'slave-01')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

class RobotSDK:
    def set_velocity(self, linear: float, angular: float):
        print(f"[SLAVE SDK] set_velocity linear={linear} angular={angular}")

    def status(self):
        return {'ts': time.time(), 'battery': 0.8}

sdk = RobotSDK()


def on_cmd(data):
    payload = data.get('payload', {})
    sdk.set_velocity(payload.get('linear', 0), payload.get('angular', 0))


def on_exec(data):
    print('[SLAVE EXEC]', data)


def status_provider():
    return {'role': 'slave', **sdk.status()}


def main():
    client = WsClient(ROBOT_ID, WS_URL, AUTH_TOKEN, on_cmd=on_cmd, on_exec=on_exec, status_provider=status_provider)
    import asyncio
    asyncio.run(client.run())

if __name__ == '__main__':
    main()
