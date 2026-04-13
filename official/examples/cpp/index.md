# C++ 示例总览

这组示例更适合对照 SDK 类型定义、查看完整调用链和参考工程化写法。

## 构建与运行

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
ros2 run examples 对应功能名称
```

## 控制类

- [获取机器人模式](/official/examples/cpp/robot-mode-get)
- [设置机器人模式](/official/examples/cpp/robot-mode-set)
- [设置机器人动作](/official/examples/cpp/robot-action-set)
- [夹爪控制](/official/examples/cpp/gripper)
- [灵巧手控制](/official/examples/cpp/hand)
- [注册二开输入源](/official/examples/cpp/input-register)
- [获取当前输入源](/official/examples/cpp/input-get)
- [机器人走跑控制](/official/examples/cpp/locomotion)
- [关节电机控制](/official/examples/cpp/joint)
- [键盘控制机器人](/official/examples/cpp/motion-keyboard)

## 感知类

- [拍照](/official/examples/cpp/camera-photo)
- [相机推流示例集](/official/examples/cpp/camera-stream)
- [头部触摸传感器数据订阅](/official/examples/cpp/touch-sensor)
- [激光雷达数据订阅](/official/examples/cpp/lidar)

## 交互类

- [播放视频](/official/examples/cpp/video-playback)
- [媒体文件播放](/official/examples/cpp/media-playback)
- [TTS（文字转语音）](/official/examples/cpp/tts)
- [麦克风数据接收](/official/examples/cpp/microphone)
- [表情控制](/official/examples/cpp/emoji)
- [LED 灯带控制](/official/examples/cpp/led)

## 说明

- C++ 版本更方便追踪消息类型、服务定义和细节实现
- 示例主要用于接口演示，建议按你自己的工程结构封装
- 需要快速验证时，可切回 [Python 示例总览](/official/examples/python/)
