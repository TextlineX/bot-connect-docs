# 远程调试与同步

## 1. 网络与 SSH 准备
- **有线直连**：
  - 上位机网口设置：`10.0.1.2/24`（掩码 `255.255.255.0`）。
  - 机器人默认 IP：`10.0.1.41`。
  - 连接测试：`ping 10.0.1.41` 和 `ssh agi@10.0.1.41`。
- **Wi-Fi 连接(推荐)**：
  - IP：`192.168.88.88`。
  - 若提示 host key 变更,则需要移除缓存：`ssh-keygen -f "$HOME/.ssh/known_hosts" -R "192.168.88.88"`。

## 2. 源码同步(可选，可以快速将sdk上传到机器)
使用 `rsync` 将本地代码同步到机器人。建议在机器人端先创建目录：
```bash
ssh agi@192.168.88.88 "mkdir -p /agibot/data/home/agi/aimdk/src"
```
同步命令：
```bash
rsync -avz --delete src/ agi@192.168.88.88:/agibot/data/home/agi/aimdk/src/
rsync -avz package*.json README.md setup.sh docs/ agi@192.168.88.88:/agibot/data/home/agi/aimdk/
```
*注意：可使用 `--exclude build --exclude install --exclude log` 减少传输量。*

## 3. 机器人端构建
1. 切换目录并配置 ROS 环境：
```bash
cd /agibot/data/home/agi/aimdk
source /opt/ros/humble/setup.bash
```
2. 安装依赖并编译：
```bash
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select <你的包名>
source install/local_setup.bash
```

## 4. 远程调试
- **建立端口转发**：`ssh -L 5678:localhost:5678 agi@10.0.1.41`。(请在有限模式使用)
- **机器人端启动调试模式**：
```bash
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client $(which ros2) run <包名> <节点名>
```
- **VS Code 配置**(推荐开发模式)：在 `launch.json` 中添加 `attach` 配置，并将 `${workspaceFolder}/src` 映射到 `/agibot/data/home/agi/aimdk/src`。
