# Bot Connect 全流程文档

## 目录结构
```
bot_connect/
├─ backend/          # Node WebSocket 路由服务器
├─ frontend/         # Vue 控制台
├─ common/           # ws_client.py, tts_client.py
├─ master/           # 主机客户端（cmd_vel + TTS + result 回传）
└─ slave/            # 从机示例
```
机器人侧同步到 `/agibot/data/home/agi/bot_connect/...`

---
## PC 端
### 后端 (Node)
```
cd H:\Project\Bot\bot_connect\backend
npm install
node server.js   # ws://0.0.0.0:8765
```
可选环境：WS_HOST / WS_PORT / AUTH_TOKEN

### 前端 (Vue + Vite)
```
cd H:\Project\Bot\bot_connect\frontend
npm install
npm run dev -- --host --port 5173
```
浏览器：`http://<PC_IP>:5173`，WS 地址填 `ws://<PC_IP>:8765`。
功能：发送 cmd_vel，发送 TTS（action=tts），显示 result 回调；ASR 面板显示 asr_text；录音面板可录制/上传 audio_upload。

---
## 机器人主机
### 环境
```
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
pip install websockets   # 如未装
```

### 主机客户端 (master/client.py)
- 处理 cmd_vel；处理 exec.action==tts，调用 PlayTts，并通过 WS 回送 result。
- 运行：
```
cd /agibot/data/home/agi/bot_connect/master
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765   # 用真实 PC IP，去掉尖括号
export ROBOT_ID=master-01
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts   # 如服务名不同替换
python client.py
```

### 通用模块 (common)
- ws_client.py：WebSocket 客户端封装
- tts_client.py：封装 PlayTts，支持 `TTS_SERVICE`

### 可选：话题触发 TTS 代理 (x2_bot/tts_proxy)
```
cd ~/aimdk
source /opt/ros/humble/setup.bash
colcon build --packages-select x2_bot
source install/setup.bash
ros2 run x2_bot tts_proxy --ros-args -p tts_service:=/aimdk_5Fmsgs/srv/PlayTts
# 测试
ros2 topic pub /ws_bridge/tts_proxy std_msgs/String "data: '你好，测试 TTS'" -1
```

---
## 机器人从机（示例）
```
cd /agibot/data/home/agi/bot_connect/slave
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765   # 用真实 PC IP
export ROBOT_ID=slave-01
python client.py
```

---
## 常见排查
- 后端日志 `target ... offline`：主机/从机未连上后端。
- TTS failed/timeout：`ros2 service list | grep PlayTts`；`TTS_SERVICE` 是否匹配；是否已 source 环境。
- 前端连不上：确认 `node server.js` 在跑、防火墙放行 8765、WS_URL IP 正确。

---
## 文件清单（保留）
- backend: server.js, package.json
- frontend: package.json, vite.config.js, index.html, src/**/*
- common: ws_client.py, tts_client.py
- master: client.py
- slave: client.py
- docs: pc.md, robot_master.md, robot_slave.md, structure.md, 总览 docs.md
```
