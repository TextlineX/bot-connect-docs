# 机器人端（主机）

## 环境准备
```
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
pip install websockets   # 如未装
```

## 主机客户端 (master/client.py)
- 处理 cmd_vel；处理 exec.action==tts，调用 PlayTts，并通过 WS 回送 result。
- 运行：
```
cd /agibot/data/home/agi/bot_connect/master
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ID=master-01
export TTS_SERVICE=/aimdk_5Fmsgs/srv/PlayTts   # 如服务名不同替换
python client.py
```

## 通用模块 (common)
- ws_client.py：WebSocket 客户端封装
- tts_client.py：封装 PlayTts，支持环境变量 `TTS_SERVICE`

## 可选：话题触发 TTS 代理 (x2_bot/tts_proxy)
```
cd ~/aimdk
source /opt/ros/humble/setup.bash
colcon build --packages-select x2_bot
source install/setup.bash
ros2 run x2_bot tts_proxy --ros-args -p tts_service:=/aimdk_5Fmsgs/srv/PlayTts
# 测试
ros2 topic pub /ws_bridge/tts_proxy std_msgs/String "data: '你好，测试 TTS'" -1
```

## 常见问题
- `target ... offline`：主机未连后端，检查 WS_URL/IP。
- `TTS failed/timeout`：检查 `ros2 service list | grep PlayTts`、`TTS_SERVICE`、是否 source 环境。
