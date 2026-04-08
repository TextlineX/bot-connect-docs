import asyncio
import json
import os
import time

import websockets

# 环境变量可调：
#   WS_URL    默认 ws://127.0.0.1:8765
#   TARGET    默认 master-01
#   LIN       默认 0.2
#   ANG       默认 0.1
#   ROBOT_ID  默认 controller
url = os.getenv("WS_URL", "ws://127.0.0.1:8765")
target = os.getenv("TARGET", "master-01")
lin = float(os.getenv("LIN", "0.2"))
ang = float(os.getenv("ANG", "0.1"))
rid = os.getenv("ROBOT_ID", "controller")


async def main():
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"type": "hello", "robot_id": rid, "ts": time.time()}))
        cmd = {
            "type": "cmd_vel",
            "robot_id": rid,
            "target_robot": target,
            "payload": {"linear": lin, "angular": ang},
            "ts": time.time(),
        }
        await ws.send(json.dumps(cmd))
        print("sent", cmd)


if __name__ == "__main__":
    asyncio.run(main())
