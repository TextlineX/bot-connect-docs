# 环境搭建

## PC 端环境

### Node.js（后端 + 前端构建）

```bash
# Windows: https://nodejs.org 下载 LTS 版本
# 验证
node -v   # >= 18
npm -v
```

### Python（ASR Worker / 机器人客户端）

```bash
# Windows: https://www.python.org 下载 3.10+
# 验证
python --version
pip install websockets
```

### ffmpeg（音频转码）

```bash
# Windows: https://ffmpeg.org/download.html
# 或 winget install ffmpeg
ffmpeg -version
```

### Vosk（可选，本地 ASR）

```bash
# 下载模型
# https://alphacephei.com/vosk/models
# 解压到本地，设置 MODEL_PATH 环境变量
```

## 机器人端环境

### ROS 2 Humble

```bash
# 参考官方安装指南
source /opt/ros/humble/setup.bash
```

### AIMDK SDK

```bash
source /agibot/data/home/agi/aimdk/install/setup.bash
```

### 依赖

```bash
pip install websockets
sudo apt install -y ffmpeg
```
