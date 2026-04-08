# Bot Connect 操作文档

## 目录结构
- backend/  
  Node WebSocket 服务器，负责路由消息。
- frontend/ 
  Vue 控制台，发指令/查看回调。
- common/   
  通用模块：
  - ws_client.py：WebSocket 客户端封装
  - tts_client.py：PlayTts 服务封装
- master/   
  主机客户端，处理 cmd_vel 与 exec.tts，回传 result。
- slave/    
  从机示例客户端（占位，可按需扩展）。

机器人侧同步后路径示例：`/agibot/data/home/agi/bot_connect/...`

---
## 前后端栈与启动

### 后端 (Node)
- 位置：backend/
- 启动：
  ```powershell
  cd H:\Project\Bot\bot_connect\backend
  npm install
  node server.js   # 监听 ws://0.0.0.0:8765
  ```
- 环境变量：WS_HOST/WS_PORT/AUTH_TOKEN（可选）。

### 前端 (Vue + Vite)
- 位置：frontend/
- 启动：
  ```powershell
  cd H:\Project\Bot\bot_connect\frontend
  npm install
  npm run dev -- --host --port 5173
  ```
- 浏览器：`http://<PC_IP>:5173`，WS 地址填 `ws://<PC_IP>:8765`。
- 功能：发送 cmd_vel、发送 TTS（action: tts），日志显示 result 回调。

---
## 机器人主机端

### 环境准备
```bash
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
pip install websockets   # 如未装
```

### 主机客户端 (master/client.py)
- 行为：
  - 连接后端；处理 cmd_vel。
  - 处理 exec.action==tts，调用 PlayTts（默认服务名 `/aimdk_5Fmsgs/srv/PlayTts`）；
    将结果通过 `type: result` 回送前端。
- 运行：
  ```bash
  cd /agibot/data/home/agi/bot_connect/master
  source /opt/ros/humble/setup.bash
  source /agibot/data/home/agi/aimdk/install/setup.bash
  export WS_URL=ws://<PC_IP>:8765
  export ROBOT_ID=master-01
  export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts  # 如服务名不同替换
  python client.py
  ```

### 通用模块 (common)
- ws_client.py：WebSocket 客户端封装。
- tts_client.py：封装 PlayTts 调用，支持环境变量 `TTS_SERVICE`。

### 可选 TTS 代理 (x2_bot/tts_proxy)
- 订阅 `/ws_bridge/tts_proxy`，调用 PlayTts。
- 构建/运行：
  ```bash
  cd ~/aimdk
  source /opt/ros/humble/setup.bash
  colcon build --packages-select x2_bot
  source install/setup.bash
  ros2 run x2_bot tts_proxy --ros-args -p tts_service:=/aimdk_5Fmsgs/srv/PlayTts
  ```
- 测试：`ros2 topic pub /ws_bridge/tts_proxy std_msgs/String "data: '你好，测试 TTS'" -1`

---
## 从机端 (可选示例)
```bash
cd /agibot/data/home/agi/bot_connect/slave
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ID=slave-01
python client.py
```

---
## 常见排查
- 后端日志出现 `target ... offline`：主机/从机未连接后端。
- TTS failed/timeout：
  1) `ros2 service list | grep PlayTts` 是否有服务；
  2) `TTS_SERVICE` 是否匹配；
  3) 已 source ROS 环境。
- 前端连不上：确认 `node server.js` 在跑、Windows 防火墙放行 8765、`WS_URL` IP 正确。
