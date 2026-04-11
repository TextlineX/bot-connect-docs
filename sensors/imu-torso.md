# 🧭 传感器详细档案：躯干惯导 (Torso IMU)

## 📡 基础通信参数
- 话题：`/aima/hal/imu/torso/state`
- 类型：`sensor_msgs/msg/Imu`
- QoS：未见特别设置，默认可靠/volatile 可用。

## 📊 运行特性（实测）
- 发布频率：≈494 Hz（高频）
- 字段：orientation, angular_velocity, linear_acceleration（标准 Imu）

## ⚠️ 使用提示
1. 高频 500 Hz 等级，回调只做缓存，后置定时器（20–50 Hz）消费。
2. 与雷达 IMU/胸部 IMU 做时间同步时，优先使用时间戳对齐而非消息序号。
3. 如需降频发布，建议在节点内做下采样而非在回调里做重计算。
