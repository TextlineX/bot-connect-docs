# 基于 asyncio 的轻量 WebSocket 路由服务器
# 用法：python server.py
# 环境变量：
#   WS_HOST (默认 0.0.0.0)
#   WS_PORT (默认 8765)
#   AUTH_TOKEN (可选，客户端需在 hello 中携带)
# 生产建议：放到 systemd / pm2，前面用 NGINX/Caddy 反代并启用 TLS。

import asyncio
import json
import logging
import os
import signal
from typing import Dict

import websockets

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
)

HOST = os.getenv('WS_HOST', '0.0.0.0')
PORT = int(os.getenv('WS_PORT', '8765'))
AUTH_TOKEN = os.getenv('AUTH_TOKEN')  # 可选
PING_INTERVAL = 20
PING_TIMEOUT = 20

# robot_id -> websocket
clients: Dict[str, websockets.WebSocketServerProtocol] = {}

async def register(ws, hello_msg: dict):
    robot_id = hello_msg.get('robot_id')
    token = hello_msg.get('token')
    if not robot_id:
        raise ValueError('missing robot_id')
    if AUTH_TOKEN and token != AUTH_TOKEN:
        raise ValueError('invalid token')
    clients[robot_id] = ws
    logging.info('robot %s connected, %d online', robot_id, len(clients))
    await ws.send(json.dumps({'type': 'ack', 'robot_id': robot_id}))
    return robot_id

async def unregister(robot_id: str):
    if robot_id and clients.get(robot_id):
        clients.pop(robot_id, None)
        logging.info('robot %s disconnected, %d online', robot_id, len(clients))

async def route_message(robot_id: str, data: dict):
    """简单路由：如果含 target_robot 就转发，否则打印（可改成落库/推送前端）。"""
    target = data.get('target_robot')
    if target:
        ws = clients.get(target)
        if ws:
            await ws.send(json.dumps(data))
        else:
            logging.warning('target %s offline, drop msg type=%s', target, data.get('type'))
    else:
        logging.info('recv %s: %s', robot_id, data.get('type'))

async def handler(ws, path):
    robot_id = None
    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=PING_TIMEOUT)
        hello = json.loads(raw)
        if hello.get('type') != 'hello':
            raise ValueError('first message must be hello')
        robot_id = await register(ws, hello)

        async for raw in ws:
            try:
                data = json.loads(raw)
                await route_message(robot_id, data)
            except Exception as e:
                logging.warning('handle error from %s: %s', robot_id, e)
    except Exception as e:
        logging.warning('connection init failed: %s', e)
    finally:
        await unregister(robot_id)

async def main():
    stop = asyncio.Future()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: stop.set_result(True))

    server = await websockets.serve(
        handler, HOST, PORT,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT,
        max_size=2 * 1024 * 1024,
    )
    logging.info('WebSocket server on %s:%d', HOST, PORT)
    await stop
    server.close()
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
