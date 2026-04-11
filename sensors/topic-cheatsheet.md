# 常用话题速查表

下表汇总了机器人各系统模块对应的常用 ROS 2 话题。

| 类别 | 话题 | 说明 |
| :--- | :--- | :--- |
| **🦾 关节状态** | `/aima/hal/joint/[group]/state` | 类型实测为 `aimdk_msgs/msg/JointStateArray`（arm/head/leg/waist），hand 为 `aimdk_msgs/msg/HandStateArray` |
| | `/aima/hal/joint/[group]/command` | 关节控制指令（类型未现场确认） |
| | *关节组 [group]* | `arm`, `hand`, `head`, `leg`, `waist` |
| **🧭 IMU 惯性** | `/aima/hal/imu/chest/state` | 胸部惯导 (主要用于平衡) |
| | `/aima/hal/imu/torso/state` | 躯干惯导 |
| **📷 视觉感知** | `/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed` | 前右立体相机图像，约 10 Hz；camera_info 低频/按需 |
| | `/aima/hal/sensor/rgbd_head_front/rgb_image/compressed` | 前方 RGB-D 相机图像（低频/按需） |
| | `/aima/hal/sensor/rgb_head_rear/rgb_image/compressed` | 后方单目相机图像，约 10 Hz |
| **📡 激光雷达** | `/aima/hal/sensor/lidar_chest_front/lidar_raw_data` | 类型 `aimdk_msgs/msg/LidarRawData`（自定义原始数据，需自行转 PointCloud2） |
| | `/aima/hal/sensor/lidar_chest_front/imu` | 雷达内置 IMU，实测≈200 Hz |
| **🔋 电池电源** | `/aima/battery_state/pb_3Aaimdk_2Eprotocol_2EBmsState` | 实际类型 `ros2_plugin_proto/msg/RosMsgWrapper`（封装 Protobuf） |
| | `/aima/hal/pmu/state` | 类型 `aimdk_msgs/msg/PmuState` |
| **🤖 运动控制** | `/aima/mc/locomotion/velocity` | 类型 `aimdk_msgs/msg/McLocomotionVelocity` |
| | `/aima/mc/body_pose` | 类型 `aimdk_msgs/msg/McBodyPose` |
| | `/aima/mc/common/state` | 类型 `aimdk_msgs/msg/McCommonState` |
| **🏥 监控诊断** | `/aima/hds/monitor/info` | 类型 `aimdk_msgs/msg/HdsMonitor` |
| | `/aima/hal/monitor/ddcu` / `udcu` | DDCU/UDCU 监控数据 |
| **🎤 语音音频** | `/aima/hal/audio/capture` | 类型 `aimdk_msgs/msg/AudioCapture`，RELIABLE/VOLATILE，当前未见数据发布 |
| | `/aima/hal/audio/playback` | 类型 `aimdk_msgs/msg/AudioPlayback`，有订阅者（hal_audio），等待上游发布 |
| | `/agent/process_audio_output` | 类型 `aimdk_msgs/msg/ProcessedAudioOutput`，有发布者 aimrt_agent_node |

## 常用查询命令
- **查看话题信息**: `ros2 topic info <topic_name> -v`
- **查看实时数据**: `ros2 topic echo <topic_name> --field <field_name>`
- **查看发布频率**: `ros2 topic hz <topic_name>`
- **可视化图像**: `ros2 run rqt_image_view rqt_image_view`
- **可视化点云**: 在 `rviz2` 中添加 `PointCloud2` 并选择对应话题。

## 特别提示
- **QoS 策略**: 部分话题（如 IMU 和激光雷达）可能使用 `TRANSIENT_LOCAL` 或 `BEST_EFFORT`，订阅时请务必确认。
- **频宽警告**: 视觉数据建议优先订阅 `/compressed` 话题以节省网络带宽。
