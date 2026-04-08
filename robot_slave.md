# 机器人端（从机示例）

## 运行
```
cd /agibot/data/home/agi/bot_connect/slave
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
export WS_URL=ws://<PC_IP>:8765
export ROBOT_ID=slave-01
python client.py
```

默认仅打印 cmd_vel，可按需扩展（参考 master/client.py）。
