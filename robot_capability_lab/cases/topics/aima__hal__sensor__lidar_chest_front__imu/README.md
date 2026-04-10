# topic 测试项

- 名称: `/aima/hal/sensor/lidar_chest_front/imu`
- 分类: `lidar`
- 类型: `sensor_msgs/msg/Imu`
- 文档状态: `已文档化`
- 项目状态: `not_connected`

## 文档来源

- `知识库/官方/5_interface/hal/sensor.md` | IMU话题
- `知识库/官方/5_interface/hal/sensor.md` | Lidar话题

## 推荐命令

```bash
ros2 topic info /aima/hal/sensor/lidar_chest_front/imu -v
ros2 topic type /aima/hal/sensor/lidar_chest_front/imu
ros2 interface show sensor_msgs/msg/Imu
# 高带宽话题，默认先跑: ros2 topic hz /aima/hal/sensor/lidar_chest_front/imu
# 若确认安全，再手工采样: ros2 topic echo /aima/hal/sensor/lidar_chest_front/imu --once
```

## 测试记录

- 首次验证时间: 
- 机器人环境: 
- 是否存在: 
- 实际类型: 
- QoS / 频率: 
- 样本是否拿到: 
- 结论: 
- 备注: 
