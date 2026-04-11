# 同步与运行指南

## 代码同步到机器人

```bash
# 从 PC 同步到机器人（WSL）
./scripts/sync_to_robot.sh

# 或 PowerShell
.\scripts\sync_to_robot.ps1
```

## 一键启动脚本

| 脚本 | 用途 |
|------|------|
| `start_relay.ps1` | PC 端：后端 + 前端 |
| `start_full_stack.ps1` | PC 端：后端 + 前端 + Master 模拟 |
| `start_master.sh` | 机器人：Master 客户端 |
| `start_slave.sh` | 机器人：Slave 客户端 |
| `start_slave_camera_stream.sh` | 机器人：Slave + 摄像头推流 |

## 环境变量速查

### Master

| 变量 | 说明 |
|------|------|
| `WS_URL` | PC 后端地址 |
| `ROBOT_ID` | 机器人标识 |
| `SIM_MODE` | `1` 模拟，`0` 真机 |
| `TTS_SERVICE` | TTS 服务名 |
| `MASTER_MODULES` | 启用的模块 |

### Slave

| 变量 | 说明 |
|------|------|
| `WS_URL` | PC 后端地址 |
| `ROBOT_ID` | 机器人标识 |
| `SIM_MODE` | `1` 模拟，`0` 真机 |
| `STREAM_AUTOSTART` | `1` 自动启动推流 |
| `STREAM_PUBLIC_HOST` | 机器人 IP（供前端访问） |
| `STREAM_TOPIC` | 相机 ROS 话题 |
