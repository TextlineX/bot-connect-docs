# 远程调试与同步

## 代码同步

### Windows → 机器人

```powershell
# PowerShell
.\scripts\sync_to_robot.ps1

# 或 WSL Bash
./scripts/sync_to_robot.sh
```

### rsync 同步（推荐）

```bash
rsync -avz --exclude='node_modules' --exclude='__pycache__' \
  /mnt/h/Project/Bot/bot_connect/ \
  user@robot:/agibot/data/home/agi/bot_connect/
```

## 远程调试

### Python 远程调试

```bash
# 在机器人上启动 debugpy
python -m debugpy --listen 0.0.0.0:5678 -m robot.client

# 在 PC 上用 VSCode 连接
```

### ROS 话题监听

```bash
# 在 PC 上监听机器人 ROS 话题（需网络互通）
export ROS_DOMAIN_ID=...
ros2 topic echo /cmd_vel
```
