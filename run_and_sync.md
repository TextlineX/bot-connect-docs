# Bot Connect 同步与启动指南（含 IP 标注）

## 角色与 IP 约定
- **PC（后端 + 前端 + 模拟主从）**：`<PC_IP>`（示例 `192.168.31.170`），端口：WS `8765`，前端 `5173`。
- **机器人主机（真机 master）**：`<ROBOT_MASTER_IP>`（如有），从机可共用此网段。
- WSL 访问宿主：`172.19.0.1:8765`（默认 WSL 虚拟网关）。

> 把以上占位替换成你实际网段，建议写入 `config/local.sh` 或 `config/local.ps1` 方便脚本复用。

## 一次性准备
1) 安装依赖：PC 上 `node >= 18`、`npm`、`python`，并确保 `ffmpeg` 在 PATH。  
2) 前后端依赖安装：
   ```powershell
   cd H:\Project\Bot\bot_connect\backend; npm install
   cd H:\Project\Bot\bot_connect\frontend; npm install
   ```
3) 配置文件：
   - 后端：`backend/config.json`（已包含 version 与 master/slave 目标）。
   - 主机 AI：`config/master_config.json`（API Key 等）。
   - 从机：`config/slave_config.json`（控制端 ID）。
   - 自定义环境：`config/local.sh` 或 `config/local.ps1`，写入 `WS_URL`、`MASTER_ROBOT_ID`、`SLAVE_ROBOT_ID` 等。

## 启动顺序（本地模拟）
1) **后端**（PC 上）  
   ```powershell
   cd H:\Project\Bot\bot_connect\backend
   set WS_HOST=0.0.0.0
   set WS_PORT=8765
   # ASR 默认由 master 识别；若要后端识别可设 MODEL_PATH 或 ASR_MODE=local
   node server.js
   ```
   可选：如需本地 ASR，额外 `set MODEL_PATH=<VOSK_MODEL_DIR>`。

2) **前端**（PC 上）  
   ```powershell
   cd H:\Project\Bot\bot_connect\frontend
   npm run dev -- --host --port 5173
   ```
   浏览器打开 `http://<PC_IP>:5173`，WS 地址填 `ws://<PC_IP>:8765`。

3) **主机模拟 master（WS-only）**  
   - Windows：`.\scripts\start_master_sim.ps1 -WS_URL ws://<PC_IP>:8765 -ROBOT_ID master-01`
   - Linux：`CONFIG_ENV=local ./scripts/start_master.sh`（默认 `SIM_MODE=1`，入口 `robot/client.py`）。

4) **从机模拟 slave（WS-only）**  
   - Windows：`.\scripts\start_slave_win.ps1 -WS_URL ws://<PC_IP>:8765 -RobotId slave-01`
   - Linux：`CONFIG_ENV=local ./scripts/start_slave.sh`

5) 打开前端“设置”页，确认：  
   - `大脑 master` = `master-01`，`控制 slave` = `slave-01`；  
   - 保存并同步（会写入 `backend/config.json` 且推送到 master/slave）。

## 启动顺序（真机部署）
1) **后端/前端**（仍在 PC 上）  
   按“本地模拟”第 1、2 步运行，PC IP 即真机的 WS 目标。

2) **真机 master**（机器人）  
   ```bash
   cd /agibot/data/home/agi/bot_connect
   source /opt/ros/humble/setup.bash
   source /agibot/data/home/agi/aimdk/install/setup.bash
   export WS_URL=ws://<PC_IP>:8765     # PC 的实际 IP
   export ROBOT_ROLE=master
   export ROBOT_ID=master-01
   export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts
   export MASTER_MODULES=all
   export SIM_MODE=0                   # 真机请用 0
   python robot/client.py
   ```

3) **真机 slave**（机器人，可与 master 同机或另一台）  
   ```bash
   cd /agibot/data/home/agi/bot_connect
   source /opt/ros/humble/setup.bash
   source /agibot/data/home/agi/aimdk/install/setup.bash
   export WS_URL=ws://<PC_IP>:8765
   export ROBOT_ROLE=slave
   export ROBOT_ID=slave-01
   export SIM_MODE=0                   # 无 ROS/TTS 时可临时 1，仅走 WS
   python robot/client.py
   ```

## 真机同步到机器人
> 机器人侧路径：`/agibot/data/home/agi/bot_connect`（示例，按需调整）。

- Linux/WSL 同步脚本：`./scripts/sync_to_robot.sh` 或 `./scripts/sync_to_robot_wsl.sh`  
  需在脚本内设置 `ROBOT_HOST=<ROBOT_MASTER_IP>`，默认 rsync/ssh。
- Windows 同步：`.\scripts\sync_to_robot.ps1 -RobotHost <ROBOT_MASTER_IP>`。

同步完后，在机器人上执行（示例 master）：
```bash
cd /agibot/data/home/agi/bot_connect
# 1) 激活环境（ROS + AIMDK）
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
# 2) 设定 WS / 角色 / ID / 模块
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ROLE=master            # 或 slave
export ROBOT_ID=master-01           # 从机改为 slave-01
export MODEL_PATH=/agibot/data/home/agi/models/vosk-model-small-cn-0.22   # master 识别 ASR 必填
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts
export MASTER_MODULES=all           # master 可精简模块
export SIM_MODE=0                   # 真机请设为 0
# 3) 启动
python robot/client.py
```
从机同理：`ROBOT_ROLE=slave`、`ROBOT_ID=slave-01`、`SIM_MODE=0`。若 ROS/TTS 不可用，可临时 `SIM_MODE=1` 仅走 WS。

## 常见连通检查
- 前端连不上：确认 `node server.js` 在跑、防火墙放行 `8765`、WS 地址为 `<PC_IP>` 而非 `localhost`（跨机时）。  
- 配置不同步：查看后端日志是否有 `config_sync` / `config_sync_ack`，或检查 `backend/config.json` 的 `version` 是否递增。  
- 模拟还在录音：刷新页前点击“停止录音”；当前端刷新后会自动清理挂起录音会话。  

## 角色与 IP 速查表
- 后端/前端/模拟：运行在 `<PC_IP>`，端口 WS `8765`，前端 `5173`。  
- master（真机或本地）：`ROBOT_ID=master-01`，WS 指向 `<PC_IP>:8765`。  
- slave（真机或本地）：`ROBOT_ID=slave-01`，WS 指向 `<PC_IP>:8765`。  
- WSL 访问宿主：`WS_URL=ws://172.19.0.1:8765`。  
