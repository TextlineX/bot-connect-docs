# 🤖 运动控制（MC 模块）

## 📡 基础通信参数（实测类型）
- `/aima/mc/locomotion/velocity` → `aimdk_msgs/msg/McLocomotionVelocity`
- `/aima/mc/body_pose` → `aimdk_msgs/msg/McBodyPose`
- `/aima/mc/common/state` → `aimdk_msgs/msg/McCommonState`
- QoS：未见特殊设置，默认可用。

## 📊 运行特性
- 本次批量检测未测得有效频率（可能低频或无发布场景）。需要在运动控制实际运行时再测 Hz。

## ⚠️ 使用提示
1. 以上类型与旧文档的 geometry_msgs / aima_msgs 不一致，开发时按 aimdk_msgs 解析，或在桥接层统一类型。
2. 若算法依赖 Twist/Pose 等标准类型，可在中间层做类型转换后再供上层使用。
3. 订阅 locomotion/velocity 时注意 QoS 与发布端匹配；如出现 transient_local 提示，可在订阅端显式设置 durability 兼容。
