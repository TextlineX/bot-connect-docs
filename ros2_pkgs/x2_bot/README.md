# x2_bot ROS2 包（骨架）

用途：给主机/从机共用的自定义技能（TTS、音频、动作等）提供独立包，便于后续扩展。

当前内容
- `tts_client_node.py`：调用 `/aimdk_5Fmsgs/srv/PlayTts` 的简易客户端。
- `mic_sub_node.py`：订阅音频话题 `/aima/hal/audio/capture`（可通过参数 audio_topic 覆盖），打印收到的字节长度。

安装与构建（在 WSL/ROS2 Humble 环境）
```bash
cd /mnt/h/Project/Bot/bot_connect/ros2_pkgs
colcon build --packages-select x2_bot
source install/setup.bash
```

使用 TTS 客户端
```bash
ros2 run x2_bot tts_client "你好，我是灵犀X2。"
# 或指定服务名
ros2 run x2_bot tts_client --ros-args -p tts_service:=/aimdk_5Fmsgs/srv/PlayTts

# 监听音频
ros2 run x2_bot mic_sub
# 指定话题
ros2 run x2_bot mic_sub --ros-args -p audio_topic:=/your/audio/topic
```

后续扩展建议
- 将音频解析/动作控制等节点放入 `x2_bot/` 目录，并在 `setup.py` 的 `console_scripts` 注册。
- 若需话题桥接，可新增 launch 文件或 service/action 客户端节点。
