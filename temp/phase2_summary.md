# 二阶段测试摘要

- 生成时间: `2026-04-10T14:13:20+08:00`
- 话题采样成功: `0/8`
- 查询服务成功: `0/6`
- 副作用测试: `关闭`
- 副作用测试默认跳过，计划项: `1`

## 话题采样

- `/aima/hal/imu/chest/state` | fail | `sensor_msgs/msg/Imu`
- `/aima/hal/imu/torso/state` | fail | `sensor_msgs/msg/Imu`
- `/aima/hal/sensor/touch_head` | fail | `aimdk_msgs/msg/TouchState`
- `/aima/hal/pmu/state` | fail | `aimdk_msgs/msg/PmuState`
- `/aima/mc/common/state` | fail | `aimdk_msgs/msg/McCommonState`
- `/aima/hds/monitor/info` | fail | `aimdk_msgs/msg/HdsMonitor`
- `/face_ui_proxy/status` | fail | `aimdk_msgs/msg/FaceEmojiStatus`
- `/aima/hal/joint/hand/state` | fail | `aimdk_msgs/msg/HandStateArray`

## 查询服务

- `/aimdk_5Fmsgs/srv/GetVolume` | fail | `aimdk_msgs/srv/GetVolume`
- `/aimdk_5Fmsgs/srv/GetMute` | fail | `aimdk_msgs/srv/GetMute`
- `/aimdk_5Fmsgs/srv/GetMcAction` | fail | `aimdk_msgs/srv/GetMcAction`
- `/aimdk_5Fmsgs/srv/GetCurrentInputSource` | fail | `aimdk_msgs/srv/GetCurrentInputSource`
- `/aimdk_5Fmsgs/srv/GetHandType` | fail | `aimdk_msgs/srv/GetHandType`
- `/aimdk_5Fmsgs/srv/GetAllJointState` | fail | `aimdk_msgs/srv/GetAllJointState`

## 副作用测试

- `/aimdk_5Fmsgs/srv/PlayTts` | skipped | `-`
