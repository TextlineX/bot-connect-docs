# 🧭 传感器详细档案：胸部惯导 (Chest IMU)

## 📡 基础通信参数
- **话题名称**: `/aima/hal/imu/chest/state`
- **消息类型**: `sensor_msgs/msg/Imu`
- **QoS 策略 (关键)**: 
  - `Reliability`: `RELIABLE`
  - `Durability`: `TRANSIENT_LOCAL`
  - `Depth`: `10`

## 📊 硬件性能指标
- **发布频率**: 本次测试未能测到（当时无数据），需在数据发布时再确认；同机另一 IMU（torso）实测约 494 Hz，可作为参考。
- **包含数据**:
  - `orientation`: 四元数 (x, y, z, w)
  - `angular_velocity`: 角速度 (x, y, z)
  - `linear_acceleration`: 线加速度 (x, y, z)

## ⚠️ 避坑与技术细节
1. **计算性能瓶颈**: 若频率与 torso IMU 一致（≈500 Hz），回调中应避免耗时操作，优先缓存再异步处理。
2. **缓冲机制**: 建议在回调中只做“数据存入变量”，由 20–50 Hz 的定时器统一消费。

## 💻 核心解析代码 (Python)
```python
class ImuHandler:
    def __init__(self):
        self.latest_imu = None

    def imu_callback(self, msg):
        # 极简回调，仅存储数据
        self.latest_imu = msg

    def process_loop(self):
        if self.latest_imu:
            acc = self.latest_imu.linear_acceleration
            # 处理逻辑...
```
