# 结构
# H:\Project\Bot\bot_connect
# ├─ backend        # WebSocket 服务端
# │   ├─ server.py
# │   └─ requirements.txt
# ├─ common         # 主/从共用客户端封装
# │   └─ ws_client.py
# ├─ master         # 主机示例客户端
# │   └─ client.py
# └─ slave          # 从机示例客户端
#     └─ client.py

## 快速运行
# 1) 后端
#   cd H:\Project\Bot\bot_connect\backend
#   python -m venv .venv
#   .venv\Scripts\activate
#   pip install -r requirements.txt
#   python server.py  # 默认 0.0.0.0:8765
#   可设 AUTH_TOKEN=xxx 提高安全
# 2) 主机
#   cd H:\Project\Bot\bot_connect\master
#   set WS_URL=ws://<服务器IP>:8765
#   set ROBOT_ID=master-01
#   python client.py
# 3) 从机
#   cd H:\Project\Bot\bot_connect\slave
#   set WS_URL=ws://<服务器IP>:8765
#   set ROBOT_ID=slave-01
#   python client.py

## 与 lx2501 SDK 对接
# - 查看 H:\Project\Bot\lx2501_3-v0.8.0.9\src\py_examples\py_examples\robot.py 中的控制接口
# - 把 master/slave 中的 RobotSDK 占位实现替换成实际 SDK 调用（如 set_velocity/tts/动作）
# - 如果需要 ROS 2，将 on_cmd 中的命令发布到 ROS 话题，再由 ROS 驱动实际机器人。

## 协议（JSON）
# hello:   {type:"hello", robot_id, token?, ts}
# cmd_vel: {type:"cmd_vel", robot_id, target_robot?, payload:{linear, angular}}
# status:  {type:"status", robot_id, payload:{...}}
# exec:    {type:"exec", robot_id, target_robot?, payload:{custom}}
# ping/pong 用于保活。

## TLS/反代
# - 推荐用 Caddy/NGINX 在 443 上反代到 8765，并设置 wss。
# - 打开防火墙只暴露 443/8765。

## TODO
# - 控制台/前端：可在 server.py 中把消息广播到 Web 前端；
# - 日志持久化：可接入 SQLite/Redis；
# - 鉴权：强制 AUTH_TOKEN 或 JWT。
