# 🌪️ 传感器详细档案：3D 激光雷达（胸前）

> 实测结果：系统发布的是自定义原始数据话题 **/aima/hal/sensor/lidar_chest_front/lidar_raw_data**，未发现 PointCloud2 话题。内置 IMU 话题存在且频率约 200 Hz。

## 📡 基础通信参数
- 原始数据话题：`/aima/hal/sensor/lidar_chest_front/lidar_raw_data`
- 消息类型：`aimdk_msgs/msg/LidarRawData`（自定义格式）
- 内置 IMU：`/aima/hal/sensor/lidar_chest_front/imu`，类型 `sensor_msgs/msg/Imu`

## 📊 运行特性
- 原始数据频率：本次测试未可靠测得（需要驱动端确认）；内置 IMU 实测约 204 Hz。
- 上层可选：在驱动/适配层将 `LidarRawData` 解码并发布新的 `sensor_msgs/msg/PointCloud2` 话题以便 RViz 可视化。

## ⚠️ 使用提示
1. 解码前先查看接口：`ros2 interface show aimdk_msgs/msg/LidarRawData`，确认字段后再做解析。
2. 如果算法需要 PointCloud2，请自行在节点中转换并发布新话题，而不是直接依赖当前 raw 话题。
3. 雷达 IMU 可用于时间同步，频率高于文档原假设（≈200 Hz），注意与外部 IMU 对齐时间戳。
