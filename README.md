# bot_connect 使用说明（本机 / 模拟 / ROS 实机）

本仓库同时包含 **WebSocket 中转后端 + 前端可视化 + 主机 / 从机 WS 客户端 + ASR 工具**。本文按组件和场景给出一键命令。

## 目录速览
- `backend/`：WS 中转 + 音频保存 + 本地 Vosk 识别（Python worker）。上传的音频保存在 `backend/uploads/`。
- `frontend/`：Vue 界面，标签页：连接、运动、TTS、ASR、日志。ASR 页会显示收到的 `asr_text`。
- `master/`：主机 WS 客户端；自动检测 ROS/TTS，失败则退化为纯 WS 模拟。
- `docs/master_modules.md`：主机能力模块清单与知识库映射。
- `slave/`：从机 WS 客户端（纯 WS）。
- `common/`：WS 客户端公用代码。
- `asr/`：辅助脚本（`send_mock_audio.py` 发送测试音频；旧版 WS-ASR 可忽略）。
- `tools/`：`record_once_upload.py`（有麦克风时在机器人上录一次并上传）。
- `scripts/`：一键启动脚本（Windows PowerShell / WSL Bash）。

## 一键启动（推荐）
在 PowerShell（仓库根 `H:\Project\Bot\bot_connect`）：
```powershell
# 修改模型/端口可选参数
.\scripts\start_relay.ps1 -ModelPath "H:\models\vosk-model-small-cn-0.22" -PythonBin "C:\Python314\python.exe" -WsPort 8765 -DevPort 5173
```
效果：起两个窗口 —— `backend/server.js`（含本地 ASR）和 `frontend`（http://<PC_IP>:5173）。前端“连接”页填 WS 地址并点连接即可。

如果想把已实现能力全部打开并一键启动主机模拟客户端：
```powershell
.\scripts\start_full_stack.ps1 -MasterModules all -SimMode 1
```
效果：起三个窗口 —— `backend`、`frontend`、`master/client.py`。

主机 AI 服务配置写在：
```powershell
H:\Project\Bot\bot_connect\config\master_config.json
```
其中 `ai.enabled` 控制默认开关，`message` 是 AI 返回 JSON 中必须存在并用于 TTS 播报的字段。

### PC 本地全模拟（无 ROS）
1) 起后端 + 前端：同上 `start_relay.ps1`。  
2) 起主机/从机模拟：
```bash
# WSL / Git Bash
WS_URL=ws://192.168.31.170:8765 ROBOT_ID=master-01 SIM_MODE=1 /mnt/h/Project/Bot/bot_connect/scripts/start_master.sh &
WS_URL=ws://192.168.31.170:8765 ROBOT_ID=slave-01  /mnt/h/Project/Bot/bot_connect/scripts/start_slave.sh &
```
或在 Windows PowerShell：
```powershell
$env:WS_URL="ws://192.168.31.170:8765"; $env:ROBOT_ID="master-01"; $env:SIM_MODE="1"; python H:\Project\Bot\bot_connect\master\client.py
$env:WS_URL="ws://192.168.31.170:8765"; $env:ROBOT_ID="slave-01";  python H:\Project\Bot\bot_connect\slave\client.py
```
前端“连接”页选 `controller` 连接即可看到状态与日志。

## 后端（WS + 本地 ASR）
独立启动：
```powershell
cd H:\Project\Bot\bot_connect
$env:MODEL_PATH="H:\models\vosk-model-small-cn-0.22"   # 必填，Vosk 模型目录
$env:PYTHON_BIN="C:\Python314\python.exe"               # 选填，不设则用系统 python
node backend\server.js   # 默认监听 ws://0.0.0.0:8765
```
收到 `audio_upload` 会保存到 `backend\uploads\` 并送到 Python worker 识别，识别结果广播 `asr_text`，即使空结果也会发。

## 前端
```powershell
cd H:\Project\Bot\bot_connect\frontend
npm install
npm run dev -- --host --port 5173
```
或用 `.\scripts\start_frontend.ps1`。

### 前端常用功能
- “连接”页：填 `ws://<PC_IP>:8765`，Robot ID 建议填 `controller`。
- “运动”：线速度/角速度发送 `cmd_vel`。
- “TTS”：发送 `exec` 动作为 tts。
- “ASR”：显示后端广播的 `asr_text`。
- “设置 -> 主机 AI”：运行时启用或关闭主机 AI 解析，并控制 `message` 是否自动 TTS。
- “日志”：查看 WS 收到/发出的原始消息。

## 主机/从机客户端
### WSL/Ubuntu 下（有 ROS2 SDK 时）
```bash
# 1) 激活 ROS2 Humble
source /opt/ros/humble/setup.bash
# 2) 激活厂家 SDK（示例路径）
source /mnt/h/Project/Bot/lx2501_3-v0.8.0.9/install/setup.bash
# 3) 运行主机客户端
cd /mnt/h/Project/Bot/bot_connect/master
export WS_URL=ws://192.168.31.170:8765   # 改成后端 IP
export ROBOT_ID=master-01
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts
unset SIM_MODE                           # 使用 ROS/TTS
python client.py
```
若 ROS/TTS 依赖缺失，程序会自动降级为模拟模式并提示。

### 纯模拟（无 ROS，Windows 或 WSL 都可）
```bash
cd /mnt/h/Project/Bot/bot_connect/master
export WS_URL=ws://192.168.31.170:8765
export ROBOT_ID=master-01
export SIM_MODE=1     # 强制不走 ROS/TTS
export MASTER_MODULES=all
python client.py
```

### 从机
```bash
cd /mnt/h/Project/Bot/bot_connect/slave
export WS_URL=ws://192.168.31.170:8765
export ROBOT_ID=slave-01
python client.py
```
`scripts/start_master.sh` / `start_slave.sh` 已写好路径（/mnt/h/Project/...），WSL 下 `chmod +x` 后可直接用，先根据需要导出环境变量。

## 音频与 ASR 排查
- 没麦克风时可用模拟音频：`python asr/send_mock_audio.py`（用环境变量 `WS_URL` 指向后端）。
- 真实录音（机器人有麦克风时）：在机器人上运行  
  ```bash
  cd /agibot/data/home/agi/bot_connect/tools
  export WS_URL=ws://192.168.31.170:8765
  export ROBOT_ID=manual-recorder
  export DURATION=30   # 秒
  python3 record_once_upload.py
  ```
  录到的 RAW 会通过 `audio_upload` 传回后端并被识别。
- 如果后端日志看到 `audio_upload saved ...` 但前端 ASR 没显示，确认 `MODEL_PATH` 正确且 Python worker 有输出；必要时查看 `backend/uploads/<file>.raw` 自行离线解码。

## 常见问题
- `MODEL_PATH 未设置，本地识别禁用`：给后端设置 `MODEL_PATH`。
- `ws reconnect ... did not receive a valid HTTP response`：确认后端 WS 地址是否写成 PC IP，防止指向 127.0.0.1。
- ROS 服务找不到 `/aimdk_5Fmsgs/srv/PlayTts`：在机器人侧运行 `ros2 service list | grep PlayTts` 确认服务存在；若无则使用模拟模式。
- WSL 运行 `.sh` 提示 `#!/usr/bin/env: No such file`：文件存在 BOM 时会这样；已清除。如再遇到，执行 `dos2unix scripts/*.sh`。

## 变更摘要（本轮）
- 主机 `master/client.py` 支持自动检测 ROS/TTS，失败自动退化到模拟模式。
- 后端集成本地 Vosk ASR（Python worker），`audio_upload` 识别结果广播 `asr_text`。
- 新增一键脚本 `scripts/start_relay.ps1`；文档统一到本文件。
