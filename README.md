# Bot Connect 操作文档

## 目录结构
- backend/  
  Node WebSocket 服务器，负责路由消息、配置同步、音频桥接。
- frontend/ 
  Vue 控制台，区分 `master`（大脑）和 `slave`（控制端）目标。
- common/   
  通用模块：
  - ws_client.py：WebSocket 客户端封装
  - role_config.py：主从配置落盘与读取
  - tts_client.py：PlayTts 服务封装
- master/   
  主机执行逻辑（AI / ASR / 动作路由）。
- slave/    
  从机执行逻辑（控制 / TTS / 结果回传）。
- robot/
  统一机器人入口，依靠 `ROBOT_ROLE=master|slave` 切换模式。

机器人侧同步后路径示例：`/agibot/data/home/agi/bot_connect/...`

---
## 前后端栈与启动

### 后端 (Node，默认由 master 识别 ASR)
- 位置：backend/
- 依赖：`npm install`（首次）
- 运行：
  ```powershell
  cd H:\Project\Bot\bot_connect\backend
  # 如需后端本地识别，设置 MODEL_PATH 或 ASR_MODE=local；默认 ASR_MODE=master 由主机识别
  # set MODEL_PATH=H:\models\vosk-model-small-cn-0.22
  # set ASR_MODE=master | local | off
  node server.js                                       # 监听 ws://0.0.0.0:8765
  ```
- 需要本机可用 `ffmpeg`（用于 webm/mp3/ogg 等转码）。  
- WS_HOST / WS_PORT / AUTH_TOKEN 可选。
- 配置文件：`backend/config.json` 作为前端/后端/主从统一配置源，带 `version`。
- 行为：保存上传音频 -> ffmpeg 转 16k mono PCM；ASR 默认由 master 执行，后端仅转发；若设置 `MODEL_PATH` 则由后端本地 Vosk 识别并广播 `asr_text`。

#### 快速单文件测试
```powershell
set WS_URL=ws://192.168.31.170:8765
set ROBOT_ID=controller
python scripts\send_audio_ws.py test.wav   # 本地直连 WS 发送音频
```
或离线校验文件能否被识别：
```powershell
set MODEL_PATH=H:\models\vosk-model-small-cn-0.22
python scripts\test_asr_file.py backend\uploads\xxxx.raw --mime audio/pcm
```

### 前端 (Vue + Vite)
- 位置：frontend/
- 启动：
  ```powershell
  cd H:\Project\Bot\bot_connect\frontend
  npm install
  npm run dev -- --host --port 5173
  ```
- 浏览器：`http://<PC_IP>:5173`，WS 地址填 `ws://<PC_IP>:8765`。
- 功能：控制命令默认发给 `slave`，录音/ASR/AI 默认发给 `master`，并通过设置页统一同步配置。

---
## 机器人主机端

### 环境准备
```bash
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
pip install websockets   # 如未装
```

### 统一机器人入口 (robot/client.py)
- 现在建议统一用 `robot/client.py` 启动，`ROBOT_ROLE=master|slave` 决定运行模式。
- `master/client.py` 和 `slave/client.py` 仍保留各自执行逻辑，但启动入口已统一。

### 主机客户端 (master/client.py)
- 行为：
  - 连接后端；负责 ASR / AI / 动作路由（ASR 使用 `MODEL_PATH` 指向的 Vosk 模型）。
  - 收到 `config_sync` 后会把主机配置落盘到 `config/master_config.json`。
  - 处理 exec.action==tts / action_router，将结果通过 `type: result` 回送前端。
- 运行：
```bash
cd /agibot/data/home/agi/bot_connect/master
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ID=master-01
export ROBOT_ROLE=master
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts  # 如服务名不同替换
python ../robot/client.py
```

### Windows 一键模拟（仅 WS，不调用 ROS/TTS）
```powershell
cd H:\Project\Bot\bot_connect
.\scripts\start_master_sim.ps1   # 默认 WS_URL=ws://192.168.31.170:8765, ROBOT_ID=master-01
```
（需按需修改脚本里的默认地址）

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
cd /agibot/data/home/agi/bot_connect
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ID=slave-01
export ROBOT_ROLE=slave
# 默认会同时打开视频流（mediamtx + camera_rtsp_relay），如需关闭设 STREAM_ENABLE=0
# 若摄像头话题输出 H.264 压缩帧，设 STREAM_INPUT_FORMAT=h264
export STREAM_ENABLE=1
python robot/client.py   # 或直接 ./scripts/start_slave.sh（已内置推流）
```

- 从机配置会落盘到 `config/slave_config.json`。

### 从机摄像头实时流（RTSP + WebRTC）
- 适用场景：机器人从机把 ROS 2 相机话题发布成 `RTSP`，再由 `MediaMTX` 自动转成浏览器可播放的 `WebRTC/WHEP`。
- 新增脚本：
  - `scripts/camera_rtsp_relay.py`：订阅 `sensor_msgs/msg/CompressedImage` 并推到 RTSP。
  - `scripts/start_slave_camera_stream.sh`：一键启动 `MediaMTX + RTSP relay`。
- 运行前准备：
  ```bash
  source /opt/ros/humble/setup.bash
  source /agibot/data/home/agi/aimdk/install/setup.bash
  ```
- 需要安装的依赖：
  - Python：只需要项目原本的 `websockets`
  - 系统二进制：`ffmpeg`、`mediamtx`
  - ROS 环境：`rclpy`、`sensor_msgs`（通常随 ROS 2 / AIMDK 提供）
- Python 依赖安装：
  ```bash
  python3 -m pip install -U pip
  python3 -m pip install websockets
  ```
- `ffmpeg` 安装（Ubuntu / Debian）：
  ```bash
  sudo apt update
  sudo apt install -y ffmpeg
  ffmpeg -version
  ```
- `MediaMTX` 安装：
  - 到官方 Releases 页面下载对应架构的压缩包
  - 常见架构：`amd64` / `arm64` / `armv7`
  - 解压并安装到 PATH，例如：
  ```bash
  mkdir -p ~/opt/mediamtx
  tar -xzf mediamtx_<版本>_linux_<架构>.tar.gz -C ~/opt/mediamtx
  sudo install ~/opt/mediamtx/mediamtx /usr/local/bin/mediamtx
  mediamtx --version
  ```
- 第一次执行建议补权限：
  ```bash
  cd /agibot/data/home/agi/bot_connect
  chmod +x scripts/start_slave_camera_stream.sh
  ```
- 最小启动：
  ```bash
  cd /agibot/data/home/agi/bot_connect
  export ROBOT_ID=slave-01
  export STREAM_PUBLIC_HOST=<机器人IP>
  export STREAM_TOPIC=/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed
  ./scripts/start_slave_camera_stream.sh   # 或直接使用 ./scripts/start_slave.sh（默认开启推流）
  ```
- 默认输出：
  - RTSP：`rtsp://<机器人IP>:8554/slave-01`
  - WebRTC 页面：`http://<机器人IP>:8889/slave-01`
  - WHEP：`http://<机器人IP>:8889/slave-01/whep`
  - HLS：`http://<机器人IP>:8888/slave-01/index.m3u8`
- 其他常用源：
  ```bash
  export STREAM_TOPIC=/aima/hal/sensor/rgb_head_rear/rgb_image/compressed
  export STREAM_TOPIC=/aima/hal/sensor/rgbd_head_front/rgb_image/compressed
  export STREAM_QOS_RELIABILITY=reliable   # RGB-D 推荐
  ```
- 常用环境变量：
  - `STREAM_PUBLIC_HOST`：前端访问流时使用的机器人 IP，建议显式设置
  - `STREAM_TOPIC`：相机话题
  - `STREAM_NAME`：流名称，默认跟 `ROBOT_ID` 一致
  - `STREAM_RTSP_PORT`：默认 `8554`
  - `STREAM_WEBRTC_PORT`：默认 `8889`
  - `STREAM_HLS_PORT`：默认 `8888`
  - `STREAM_QOS_RELIABILITY`：通常 `best_effort`；`rgbd_head_front` 建议 `reliable`
- 前端监控页现在会优先读取机器人 `status.payload.streams` 里上报的默认 `WHEP` 地址；如果监控输入框留空，会自动显示从机默认 WebRTC 画面。
- 想随从机自动拉起推流，可在启动从机时加：`export STREAM_AUTOSTART=1`（使用 `slave/client.py` 内置拉起 mediamtx + relay）

---
## 常见排查
- 后端日志出现 `target ... offline`：主机/从机未连接后端。
- 前端设置已保存但机器人没同步：检查 `config_sync` / `config_sync_ack` 是否出现，或查看 `backend/config.json` 的 `version` 是否递增。
- TTS failed/timeout：
  1) `ros2 service list | grep PlayTts` 是否有服务；
  2) `TTS_SERVICE` 是否匹配；
  3) 已 source ROS 环境。
- 前端连不上：确认 `node server.js` 在跑、Windows 防火墙放行 8765、`WS_URL` IP 正确。
- WebRTC 无画面：
  1) 先用 `ffplay rtsp://<机器人IP>:8554/<stream_name>` 确认 RTSP 已有图；
  2) 确认 `STREAM_PUBLIC_HOST` 填的是前端机器能访问到的机器人 IP；
  3) 确认 `8889/tcp` 与 `8189/udp`（如启用 TCP fallback 也包含 `8189/tcp`）未被防火墙拦截；
  4) 若使用 RGB-D，相机订阅建议设置 `STREAM_QOS_RELIABILITY=reliable`。
  5) `ffmpeg -version` 和 `mediamtx --version` 都能正常执行。
