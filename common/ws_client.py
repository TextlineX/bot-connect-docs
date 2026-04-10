# 通用 WebSocket 客户端封装，供主/从调用
import asyncio
import json
import os
import time
from typing import Optional, Callable

import websockets

class WsClient:
    def __init__(self, robot_id: str, url: str, token: Optional[str] = None,
                 on_cmd: Optional[Callable[[dict], None]] = None,
                 on_exec: Optional[Callable[[dict], None]] = None,
                 status_provider: Optional[Callable[[], dict]] = None,
                 status_period: float = 2.0,
                 on_open: Optional[Callable] = None):
        self.robot_id = robot_id
        self.url = url
        self.token = token
        self.on_cmd = on_cmd
        self.on_exec = on_exec
        self.status_provider = status_provider or (lambda: {})
        self.status_period = status_period
        self.on_open = on_open

    async def send_loop(self, ws):
        while True:
            msg = {
                'type': 'status',
                'robot_id': self.robot_id,
                'ts': time.time(),
                'payload': self.status_provider(),
            }
            await ws.send(json.dumps(msg))
            await asyncio.sleep(self.status_period)

    async def handle_message(self, ws, data: dict):
        t = data.get('type')
        if t == 'cmd_vel' and self.on_cmd:
            self.on_cmd(data)
        elif t == 'exec' and self.on_exec:
            self.on_exec(data)
        elif t == 'ping':
            await ws.send(json.dumps({'type': 'pong', 'robot_id': self.robot_id, 'ts': time.time()}))

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20) as ws:
                    hello = {'type': 'hello', 'robot_id': self.robot_id, 'ts': time.time()}
                    if self.token:
                        hello['token'] = self.token
                    await ws.send(json.dumps(hello))

                    tasks = [asyncio.create_task(self.send_loop(ws))]
                    if self.on_open:
                        tasks.append(asyncio.create_task(self.on_open(ws)))
                    async for raw in ws:
                        try:
                            data = json.loads(raw)
                            await self.handle_message(ws, data)
                        except Exception as e:
                            print('handle error', e)
                    for t in tasks:
                        t.cancel()
            except Exception as e:
                print('ws reconnect in 3s', e)
                await asyncio.sleep(3)
