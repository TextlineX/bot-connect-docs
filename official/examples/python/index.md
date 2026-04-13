# Python 示例总览

这组示例适合快速验证接口、做脚手架开发和查阅最小可运行用法。

## 构建与运行

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
ros2 run py_examples 对应功能名称
```

## 控制类

- [获取机器人模式](/official/examples/python/robot-mode-get)
- [设置机器人模式](/official/examples/python/robot-mode-set)
- [设置机器人动作](/official/examples/python/robot-action-set)
- [夹爪控制](/official/examples/python/gripper)
- [灵巧手控制](/official/examples/python/hand)
- [注册二开输入源](/official/examples/python/input-register)
- [获取当前输入源](/official/examples/python/input-get)
- [控制机器人走跑](/official/examples/python/locomotion)
- [关节电机控制](/official/examples/python/joint)
- [键盘控制机器人](/official/examples/python/motion-keyboard)

## 感知类

- [拍照](/official/examples/python/camera-photo)
- [相机推流示例集](/official/examples/python/camera-stream)
- [头部触摸传感器数据订阅](/official/examples/python/touch-sensor)
- [激光雷达数据订阅](/official/examples/python/lidar)

## 交互类

- [播放视频](/official/examples/python/video-playback)
- [媒体文件播放](/official/examples/python/media-playback)
- [TTS（文字转语音）](/official/examples/python/tts)
- [麦克风数据接收](/official/examples/python/microphone)
- [表情控制](/official/examples/python/emoji)
- [LED 灯带控制](/official/examples/python/led)

## 说明

- 官方示例偏向接口演示，不一定直接适合生产环境
- 跨板通信场景建议补充超时、重试和状态检查
- 需要对照实现时，可同时打开 [C++ 示例总览](/official/examples/cpp/)
