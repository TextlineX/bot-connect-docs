# 真机机器人启动手册（master / slave）

目标：让机器人主机或从机连上 PC 后端（WS 8765），加载 ROS + AIMDK 环境，按角色启动。

## 前置要求
- 代码已同步到机器人：默认路径 `/agibot/data/home/agi/bot_connect`。
- 机器人内有 ROS Humble 与 AIMDK 环境：
  ```bash
  source /opt/ros/humble/setup.bash
  source /agibot/data/home/agi/aimdk/install/setup.bash
  ```
- Python 依赖：`pip install websockets`（如未安装）。

## 通用环境变量
- `WS_URL`：`ws://<PC_IP>:8765`（PC 端后端地址）
- `ROBOT_ROLE`：`master` 或 `slave`
- `ROBOT_ID`：`master-01` / `slave-01`（可自定义，但前端设置需对应）
- `SIM_MODE`：`0` 真机；`1` 仅 WS（无 ROS/TTS）

### master 专用
- `TTS_SERVICE`：默认 `/aimdk_5Fmsgs/srv/PlayTts`
- `MASTER_MODULES`：`all` 或精简模块列表（逗号分隔）
- AI 配置：`config/master_config.json`（API Key、模型等）

### slave 专用
- 默认只需 `ROBOT_ROLE=slave`、`ROBOT_ID`；若无 ROS/TTS，设 `SIM_MODE=1`

## 启动命令示例
### 主机 master（真机）
```bash
cd /agibot/data/home/agi/bot_connect
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ROLE=master
export ROBOT_ID=master-01
export MODEL_PATH=/agibot/data/home/agi/models/vosk-model-small-cn-0.22   # 主机识别 ASR 必填
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts
export MASTER_MODULES=all
export SIM_MODE=0
python robot/client.py
```

### 从机 slave（真机）
```bash
cd /agibot/data/home/agi/bot_connect
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ROLE=slave
export ROBOT_ID=slave-01
export SIM_MODE=0      # 无 ROS/TTS 时设 1
python robot/client.py
```

## 网络与 IP 提示
- PC 端：后端/前端运行在 `<PC_IP>`，WS 端口 `8765`。
- WSL 访问宿主：`ws://172.19.0.1:8765`。
- 确保机器人能访问 PC 的 8765 端口（防火墙放行）。

## 配置同步
- 前端“设置”页保存后，会写入 `backend/config.json` 并通过 `config_sync` 下发到 master/slave。
- master/slave 启动时会回 `config_sync_ack`，可在后端日志或前端日志查看。

## 常见问题
- 连接不上：检查 `WS_URL` 是否用 PC 实际 IP，防火墙是否放行 8765。
- TTS 失败：`ros2 service list | grep PlayTts` 是否存在；`TTS_SERVICE` 是否匹配；已 source 环境。
- AI 未触发：确认 `config/master_config.json` 内 API Key/模型，前端设置里开启“主机 AI 解析”。
