# 6.1.14 激光雷达数据订阅

**该示例中用到了echo_lidar_data** ，通过订阅`/aima/hal/sensor/lidar_chest_front/`话题来接收机器人的激光雷达数据，支持点云数据和IMU数据两种数据类型。

**功能特点：**

  * 支持激光雷达点云数据订阅

  * 支持激光雷达IMU数据订阅

  * 实时FPS统计和数据显示

  * 可配置的topic类型选择

  * 详细的数据字段信息输出

**支持的数据类型：**

  * `PointCloud2`: 激光雷达点云数据 (sensor_msgs/PointCloud2)

  * `Imu`: 激光雷达IMU数据 (sensor_msgs/Imu)

**技术实现：**

  * 使用SensorDataQoS配置（`BEST_EFFORT` \+ `VOLATILE`）

  * 支持点云字段信息解析和显示

  * 支持IMU四元数、角速度和线性加速度数据

  * 提供详细的调试日志输出

**应用场景：**

  * 激光雷达数据采集和分析

  * 点云数据处理和可视化

  * 机器人导航和定位

  * SLAM算法开发

  * 环境感知和建图

```python
#!/usr/bin/env python3
"""
Chest LiDAR data subscription example

Supports subscribing to the following topics:
  1. /aima/hal/sensor/lidar_chest_front/lidar_pointcloud
     - Data type: sensor_msgs/PointCloud2
     - frame_id: lidar_chest_front
     - child_frame_id: /
     - Content: LiDAR point cloud data
  2. /aima/hal/sensor/lidar_chest_front/imu
     - Data type: sensor_msgs/Imu
     - frame_id: lidar_imu_chest_front
     - Content: LiDAR IMU data

You can select the topic type to subscribe via startup parameter --ros-args -p topic_type:=<type>:
  - pointcloud: subscribe to LiDAR point cloud
  - imu: subscribe to LiDAR IMU
Default topic_type is pointcloud

Examples:
  ros2 run py_examples echo_lidar_data --ros-args -p topic_type:=pointcloud
  ros2 run py_examples echo_lidar_data --ros-args -p topic_type:=imu
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import PointCloud2, Imu
from collections import deque
import time

class LidarChestEcho(Node):
    def __init__(self):
        super().__init__('lidar_chest_echo')

        # Select the topic type to subscribe
        self.declare_parameter('topic_type', 'pointcloud')
        self.topic_type = self.get_parameter('topic_type').value

        # SensorDataQoS: BEST_EFFORT + VOLATILE
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5
        )

        # Create different subscribers based on topic_type
        if self.topic_type == "pointcloud":
            self.topic_name = "/aima/hal/sensor/lidar_chest_front/lidar_pointcloud"
            self.sub_pointcloud = self.create_subscription(
                PointCloud2, self.topic_name, self.cb_pointcloud, qos)
            self.get_logger().info(
                f"✅ Subscribing LIDAR PointCloud2: {self.topic_name}")

        elif self.topic_type == "imu":
            self.topic_name = "/aima/hal/sensor/lidar_chest_front/imu"
            self.sub_imu = self.create_subscription(
                Imu, self.topic_name, self.cb_imu, qos)
            self.get_logger().info(
                f"✅ Subscribing LIDAR IMU: {self.topic_name}")

        else:
            self.get_logger().error(f"Unknown topic_type: {self.topic_type}")
            raise ValueError("Unknown topic_type")

        # Internal state
        self.last_print = self.get_clock().now()
        self.arrivals = deque()

    def update_arrivals(self):
        """Calculate received FPS"""
        now = self.get_clock().now()
        self.arrivals.append(now)
        while self.arrivals and (now - self.arrivals[0]).nanoseconds * 1e-9 > 1.0:
            self.arrivals.popleft()

    def get_fps(self):
        """Get FPS"""
        return len(self.arrivals)

    def should_print(self):
        """Control print frequency"""
        now = self.get_clock().now()
        if (now - self.last_print).nanoseconds * 1e-9 >= 1.0:
            self.last_print = now
            return True
        return False

    def cb_pointcloud(self, msg: PointCloud2):
        """PointCloud2 callback (LiDAR point cloud)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

            # Format fields info
            fields_str = " ".join(
                [f"{f.name}({f.datatype})" for f in msg.fields])

            self.get_logger().info(
                f"🟢 LIDAR PointCloud2 received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • width x height:  {msg.width} x {msg.height}\n"
                f"  • point_step:      {msg.point_step}\n"
                f"  • row_step:        {msg.row_step}\n"
                f"  • fields:          {fields_str}\n"
                f"  • is_bigendian:    {msg.is_bigendian}\n"
                f"  • is_dense:        {msg.is_dense}\n"
                f"  • data size:       {len(msg.data)}\n"
                f"  • recv FPS (1s):   {self.get_fps():1.1f}"
            )

    def cb_imu(self, msg: Imu):
        """IMU callback (LiDAR IMU)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

            self.get_logger().info(
                f"🟢 LIDAR IMU received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • orientation:     [{msg.orientation.x:.6f}, {msg.orientation.y:.6f}, {msg.orientation.z:.6f}, {msg.orientation.w:.6f}]\n"
                f"  • angular_velocity:[{msg.angular_velocity.x:.6f}, {msg.angular_velocity.y:.6f}, {msg.angular_velocity.z:.6f}]\n"
                f"  • linear_accel:    [{msg.linear_acceleration.x:.6f}, {msg.linear_acceleration.y:.6f}, {msg.linear_acceleration.z:.6f}]\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

def main(args=None):
    rclpy.init(args=args)
    try:
        node = LidarChestEcho()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**使用说明：**

```bash
# 订阅激光雷达点云数据
ros2 run py_examples echo_lidar_data --ros-args -p topic_type:=pointcloud

# 订阅激光雷达IMU数据
ros2 run py_examples echo_lidar_data --ros-args -p topic_type:=imu
```

**输出示例：**

```python
[INFO] [lidar_chest_echo]: ✅ Subscribing LIDAR PointCloud2: /aima/hal/sensor/lidar_chest_front/lidar_pointcloud
[INFO] [lidar_chest_echo]: 🟢 LIDAR PointCloud2 received
  • frame_id:        lidar_chest_front
  • stamp (sec):     1234567890.123456
  • width x height:  1 x 36000
  • point_step:      16
  • row_step:        16
  • fields:          x(7) y(7) z(7) intensity(7)
  • is_bigendian:    False
  • is_dense:        True
  • data size:       576000
  • recv FPS (1s):   10.0
```
