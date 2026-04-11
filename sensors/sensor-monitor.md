# 传感器数据监控指南

## 1. 监控原则
- **环境 source**：运行前必须 `source /agibot/data/home/agi/aimdk/install/setup.bash`。
- **DDS 跨网**：确保监控终端与机器人处于同一 DDS 网络。
- **QoS 匹配**：标注了 `TRANSIENT_LOCAL` 的话题，必须加 `--qos-durability transient_local`。

## 2. 常用监控命令

### 控制核心传感器
```bash
# 胸部 IMU (监控姿态与加速度)
ros2 topic echo /aima/hal/imu/chest/state --qos-durability transient_local --qos-reliability reliable

# 关节状态 (监控当前位置与温度)
ros2 topic echo /aima/hal/joint/leg/state
```

### 视觉与环境传感器
```bash
# 【推荐】查看压缩彩色图
ros2 topic echo /aima/hal/sensor/rgbd_head_front/rgb_image/compressed --once

# 【仅限本机】查看原始点云 (避免 WiFi 拥堵)
ros2 topic echo /aima/hal/sensor/lidar_chest_front/lidar_pointcloud --qos-durability transient_local --once
```

### 交互传感器
```bash
# 头部触摸状态监控
ros2 topic echo /aima/hal/sensor/touch_head --qos-durability transient_local --once
```

## 3. 数据解读提示
- **IMU**：观察 `linear_acceleration` 的 `z` 轴。静止时应接近 `9.8`。
- **关节**：观察 `motor_temp`（电机温度）。若超过 60℃，需警惕并检查散热。
- **触摸**：正常状态 `event_type: 1`（空闲），触摸时变为 `2`。
