# 🦾 硬件详细档案：关节执行器

> 实测结果：所有关节状态话题均使用 **aimdk_msgs** 自定义消息，而非 aima_msgs；频率多为按需/未测得。

## 📡 基础通信参数
- 指令话题（实测类型）：  
  - arm/head/leg/waist：`/aima/hal/joint/[group]/command` → `aimdk_msgs/msg/JointCommandArray`  
  - hand：`/aima/hal/joint/hand/command` → `aimdk_msgs/msg/HandCommandArray`
- 状态话题（实测类型）：  
  - arm/head/leg/waist：`/aima/hal/joint/[group]/state` → `aimdk_msgs/msg/JointStateArray`  
  - hand：`/aima/hal/joint/hand/state` → `aimdk_msgs/msg/HandStateArray`
- 关节组 `[group]`: `arm`, `hand`, `head`, `leg`, `waist`
- QoS 观察：发布端 BEST_EFFORT + TRANSIENT_LOCAL，订阅端 BEST_EFFORT + VOLATILE；注意订阅时匹配耐受不同耐久策略。

## 📊 运行特性
- 本次批量检测未测得有效频率（可能低频或暂未发布）。建议在上线前实测实际发布率再设定滤波/缓存策略。

## ⚠️ 使用提示
1. 请在订阅前确认 `aimdk_msgs/msg/JointStateArray` 字段定义（`ros2 interface show`），确保解析位置/速度/力矩字段正确映射。
2. 若需兼容历史文档的 `aima_msgs/msg/JointState`，需在桥接层做类型转换或同步更新上层依赖。
3. 下发 `command` 前先读取对应 `state` 作为初始位置，避免大幅跳变导致机械冲击。
