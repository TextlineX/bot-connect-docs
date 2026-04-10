## Dashboard 使用说明（本地联调）

### 入口
- 前端页面 `/#/dashboard`，连接后自动显示主机 / 从机状态。
- 依赖消息类型：`status`、`capabilities`、`result`、`ai_result`、`asr_text`。

### 展示数据
- **概览**：连接状态、在线数量、最近 ASR、最近 AI。
- **主机/从机分栏**：按 `robot_id` 和 `role` 自动分组。
- **运行状态**：`system`（主机名、WS 地址、运行时长、环境标签）。
- **音频 / AI**：`audio.tts_ready`、`audio.asr_bridge_ready`、`audio.audio_topic`、AI 开关。
- **运动**：当前线/角速度、最近预设动作、动作时间戳。
- **传感器（模拟字段）**：`battery_pct`、`network_pct`、`audio_level_pct`、`imu_yaw_deg`、`obstacle_distance_cm` / `lidar_distance_m` 等。

### 后端广播
- 中继已将 `status` / `capabilities` / `result` / `ai_result` 等自动广播给所有连接客户端，参见 `backend/server.js` 的 `BROADCAST_TYPES`。

### 本地模拟状态来源
- 主机：`master/client.py` 内的 `RobotSDK.status()` 注入系统/运动/音频/传感器模拟值。
- 从机：`slave/client.py` 内的 `RobotSDK.status()` 提供简化的电量、网络、雷达等模拟值。

### 接入真实机器人
- 环境变量 `MASTER_STATUS_HOOK=master.status_hook_example` 可启用可插拔的状态扩展（示例文件 `master/status_hook_example.py`）。
- 在 hook 的 `get_status()` 里填充真实字段，建议对应：
  - `sensors.battery_pct` ← 电池话题（如 `/battery_state`）
  - `sensors.imu_yaw_deg` ← IMU yaw（如 `/imu/data`）
  - `sensors.lidar_distance_m` / `sensors.obstacle_distance_cm` ← 近距离障碍或雷达
  - `motion.last_preset` / `last_motion_id` ← 最近执行的预设动作
  - `audio.tts_ready` / `audio.asr_bridge_ready` ← 实际服务可用性
- 保持字段名一致即可让 Dashboard 自动展示；未提供的字段会显示为 “—”。

### 启动方法（本地全栈）
- 仅主机：`.\scripts\start_full_stack.ps1 -MasterModules all -SimMode 1`
- 主机 + 从机：`.\scripts\start_full_stack.ps1 -MasterModules all -SimMode 1 -StartSlave`

### 接入真实机器人时
- 在各端的 `status_provider` 中填充真实字段（保持现有 key），Dashboard 会自动呈现。
