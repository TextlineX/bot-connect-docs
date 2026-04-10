# 项目能力缺口对照

- 生成时间: `2026-04-10T13:43:06+08:00`
- 接口总数: `85`
- 真实已接入: `16`
- 半接入/代理: `1`
- 需要真实 ROS 适配: `1`
- 完全未接入: `67`

## 重点结论

- 当前项目真正接到机器人原生 ROS2 的核心能力主要是 `PlayTts` 和 `SetMcPresetMotion`。
- 运动、麦克风、相机、Lidar、IMU、触摸、PMU、屏幕等接口仍需按 case 逐项验证。
- 尤其相机和高带宽传感器，知识库有文档不等于项目已经能用，必须上真机跑探测。

## 已真实桥接

- `/aimdk_5Fmsgs/srv/SetMcPresetMotion` | service | motion | SetMcPresetMotion
- `加油` | preset_action | motion | SetMcPresetMotion
- `动感光波` | preset_action | motion | SetMcPresetMotion
- `右手举手` | preset_action | motion | SetMcPresetMotion
- `右手挥手` | preset_action | motion | SetMcPresetMotion
- `右手握手` | preset_action | motion | SetMcPresetMotion
- `右手敬礼` | preset_action | motion | SetMcPresetMotion
- `右手飞吻` | preset_action | motion | SetMcPresetMotion
- `左手举手` | preset_action | motion | SetMcPresetMotion
- `左手挥手` | preset_action | motion | SetMcPresetMotion
- `左手握手` | preset_action | motion | SetMcPresetMotion
- `左手敬礼` | preset_action | motion | SetMcPresetMotion
- `左手飞吻` | preset_action | motion | SetMcPresetMotion
- `鞠躬` | preset_action | motion | SetMcPresetMotion
- `鼓掌` | preset_action | motion | SetMcPresetMotion
- `/aimdk_5Fmsgs/srv/PlayTts` | service | voice | PlayTts

## 半接入或代理

- `/aima/hal/audio/capture` | topic | audio | aimdk_msgs/msg/AudioCapture

## 已有入口但缺真实 ROS 适配

- `/aima/mc/locomotion/velocity` | topic | motion | aimdk_msgs/msg/McLocomotionVelocity

## 知识库存在但项目未接入

- `/agent/process_audio_output` | topic | audio | aimdk_msgs/msg/ProcessedAudioOutput
- `/aima/hal/audio/playback` | topic | audio | aimdk_msgs/msg/AudioPlayback
- `/aimdk_5Fmsgs/srv/GetHandType` | service | endeffector | GetHandType
- `/aima/hal/imu/chest/state` | topic | imu | sensor_msgs/msg/Imu
- `/aima/hal/imu/torso/state` | topic | imu | sensor_msgs/msg/Imu
- `/aima/hal/sensor/rgbd_head_front/imu` | topic | imu | sensor_msgs/msg/Imu
- `/aima/hal/joint/*/command` | topic | joint | JointCommandArray
- `/aima/hal/joint/*/state` | topic | joint | JointStateArray
- `/aima/hal/joint/[group]/command` | topic | joint | aimdk_msgs/msg/JointCommandArray
- `/aima/hal/joint/[group]/state` | topic | joint | aimdk_msgs/msg/JointStateArray
- `/aima/hal/joint/hand/command` | topic | joint | aimdk_msgs/msg/HandCommandArray
- `/aima/hal/joint/hand/state` | topic | joint | aimdk_msgs/msg/HandStateArray
- `/aimdk_5Fmsgs/srv/GetAllJointState` | service | joint | GetAllJointState
- `/aima/hal/sensor/lidar_chest_front/imu` | topic | lidar | sensor_msgs/msg/Imu
- `/aima/hal/sensor/lidar_chest_front/lidar_pointcloud` | topic | lidar | sensor_msgs/msg/PointCloud2
- `/aimdk_5Fmsgs/srv/LedStripCommand` | service | lights | LedStripCommand
- `/aima/mc/body_pose` | topic | motion | aimdk_msgs/msg/McBodyPose
- `/aima/mc/common/state` | topic | motion | aimdk_msgs/msg/McCommonState
- `/aimdk_5Fmsgs/srv/GetMcAction` | service | motion | GetMcAction
- `/aimdk_5Fmsgs/srv/SetMcAction` | service | motion | SetMcAction
- `/aimdk_5Fmsgs/srv/SetMcInputSource` | service | motion | SetMcInputSource
- `双手平举` | preset_action | motion | SetMcPresetMotion
- `双手打叉` | preset_action | motion | SetMcPresetMotion
- `双手比心` | preset_action | motion | SetMcPresetMotion
- `右手击掌` | preset_action | motion | SetMcPresetMotion
- `右手平举` | preset_action | motion | SetMcPresetMotion
- `右手比心` | preset_action | motion | SetMcPresetMotion
- `左手击掌` | preset_action | motion | SetMcPresetMotion
- `左手平举` | preset_action | motion | SetMcPresetMotion
- `左手比心` | preset_action | motion | SetMcPresetMotion
- `抓屁股` | preset_action | motion | SetMcPresetMotion
- `拜拜` | preset_action | motion | SetMcPresetMotion
- `拥抱` | preset_action | motion | SetMcPresetMotion
- `挠头` | preset_action | motion | SetMcPresetMotion
- `胸前右手挥手` | preset_action | motion | SetMcPresetMotion
- `胸前左手挥手` | preset_action | motion | SetMcPresetMotion
- `/aima/hds/alert_code_list` | topic | other | aimdk_msgs/msg/AlertCodeArray
- `/aima/hds/diag_code_list` | topic | other | aimdk_msgs/msg/DiagnosticInfoArray
- `/aima/hds/monitor/info` | topic | other | aimdk_msgs/msg/HdsMonitor
- `/aima/sm/system_state` | topic | other | aimdk_msgs/msg/SmSystemState
- `/aimdk_5Fmsgs/srv/GetCurrentInputSource` | service | other | GetCurrentInputSource
- `/aimdk_5Fmsgs/srv/PlayMediaFile` | service | other | PlayMediaFile
- `/aima/hal/pmu/state` | topic | power | PmuState
- `/aimdk_5Fmsgs/srv/PlayEmoji` | service | screen | PlayEmoji
- `/aimdk_5Fmsgs/srv/PlayVideo` | service | screen | PlayVideo
- `/aimdk_5Fmsgs/srv/PlayVideoGroup` | service | screen | PlayVideoGroup
- `/face_ui_proxy/status` | topic | screen | FaceEmojiStatus
- `/aima/hal/sensor/touch_head` | topic | touch | TouchState
- `/aima/hal/sensor/rgb_head_rear/camera_info` | topic | vision | sensor_msgs/msg/CameraInfo
- `/aima/hal/sensor/rgb_head_rear/rgb_image` | topic | vision | sensor_msgs/msg/Image
- `/aima/hal/sensor/rgb_head_rear/rgb_image/compressed` | topic | vision | sensor_msgs/msg/CompressedImage
- `/aima/hal/sensor/rgbd_head_front/depth_camera_info` | topic | vision | sensor_msgs/msg/CameraInfo
- `/aima/hal/sensor/rgbd_head_front/depth_image` | topic | vision | sensor_msgs/msg/Image
- `/aima/hal/sensor/rgbd_head_front/depth_pointcloud` | topic | vision | sensor_msgs/msg/PointCloud2
- `/aima/hal/sensor/rgbd_head_front/rgb_camera_info` | topic | vision | sensor_msgs/msg/CameraInfo
- `/aima/hal/sensor/rgbd_head_front/rgb_image` | topic | vision | sensor_msgs/msg/Image
- `/aima/hal/sensor/rgbd_head_front/rgb_image/compressed` | topic | vision | sensor_msgs/msg/CompressedImage
- `/aima/hal/sensor/stereo_head_front_left/camera_info` | topic | vision | sensor_msgs/msg/CameraInfo
- `/aima/hal/sensor/stereo_head_front_left/rgb_image` | topic | vision | sensor_msgs/msg/Image
- `/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed` | topic | vision | sensor_msgs/msg/CompressedImage
- `/aima/hal/sensor/stereo_head_front_right/camera_info` | topic | vision | sensor_msgs/msg/CameraInfo
- `/aima/hal/sensor/stereo_head_front_right/rgb_image` | topic | vision | sensor_msgs/msg/Image
- `/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed` | topic | vision | sensor_msgs/msg/CompressedImage
- `/aimdk_5Fmsgs/srv/GetMute` | service | voice | GetMute
- `/aimdk_5Fmsgs/srv/GetVolume` | service | voice | GetVolume
- `/aimdk_5Fmsgs/srv/SetMute` | service | voice | SetMute
- `/aimdk_5Fmsgs/srv/SetVolume` | service | voice | SetVolume
