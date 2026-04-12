<a id="id1"></a>

# 5.4.1 传感器接口

**传感器接口提供了机器人各种传感器的数据获取和控制能力，包括相机、IMU、激光雷达、触摸传感器等。**

<a id="id2"></a>

## 核心功能

<a id="id3"></a>

### 视觉传感器

  * **RGB相机** ：彩色图像获取

  * **深度相机** ：深度信息获取

  * **相机内参** ：标定参数获取

<a id="id4"></a>

### 姿态传感器

  * **IMU数据** ：加速度、角速度、姿态角

  * **陀螺仪** ：角速度测量

  * **加速度计** ：加速度测量

<a id="id5"></a>

### 环境感知传感器

  * **激光雷达** ：点云数据获取

  * **触摸传感器** ：触觉反馈

<a id="id6"></a>

## 标准传感器消息

传感器接口大多使用ROS标准传感器定义`sensor_msgs`中的消息类型:

<a id="tbl-std-sensor-msgs"></a>

传感数据类型 | 消息定义  
---|---  
相机内参 | [`CameraInfo`](<https://docs.ros.org/en/humble/p/sensor_msgs/msg/CameraInfo.html> "sensor_msgs::msg::CameraInfo")  
原始图像 | [`Image`](<https://docs.ros.org/en/humble/p/sensor_msgs/msg/Image.html> "sensor_msgs::msg::Image")  
压缩图像 | [`CompressedImage`](<https://docs.ros.org/en/humble/p/sensor_msgs/msg/CompressedImage.html> "sensor_msgs::msg::CompressedImage")  
IMU数据 | [`Imu`](<https://docs.ros.org/en/humble/p/sensor_msgs/msg/Imu.html> "sensor_msgs::msg::Imu")  
Lidar点云 | [`PointCloud2`](<https://docs.ros.org/en/humble/p/sensor_msgs/msg/PointCloud2.html> "sensor_msgs::msg::PointCloud2")  
  
<a id="imu"></a>

## IMU话题

包括独立的胸部IMU和胯部IMU, 均位于开发计算单元(PC2)   
也可使用 Lidar 和 深度相机 附带的IMU

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/imu/chest/state` | `Imu` | 胸部IMU数据 | `TRANSIENT_LOCAL` | 500Hz  
`/aima/hal/imu/torso/state` | `Imu` | 胯部IMU数据 | `TRANSIENT_LOCAL` | 500Hz  
`/aima/hal/sensor/lidar_chest_front/imu` | `Imu` | Lidar IMU数据 | `TRANSIENT_LOCAL` | 200Hz  
`/aima/hal/sensor/rgbd_head_front/imu` | `Imu` | 深度相机 IMU数据 | `RELIABLE` | 200Hz  
  
<a id="id7"></a>

## 头部触摸状态话题

支持功能:

  * 获取底层触摸事件和原始sample

  * 关闭自带的摸头杀技能(待开放)

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/sensor/touch_head` | `TouchState` | 头部触摸状态 | `TRANSIENT_LOCAL` | 100Hz  
  
  * `TouchState` ros2-msg @ hal/msg/TouchState.msg

```
# 头部触摸状态
# 话题名称: /aima/hal/sensor/touch_head

MessageHeader header             # 消息头
uint8 event_type                 # 触摸事件 (0-未知,1-空闲,2-触摸,3-滑动,4-单击,5-双击,6-三击)
uint32[8] data                   # 8个通道的原始传感器数值
uint32[8] threshold              # 8个通道对应的触摸阈值
bool[8] is_touched               # 8个通道的触摸状态
```

<a id="rgb"></a>

## 后视RGB相机话题

后视RGB相机位于开发计算单元(PC2), 可用于视觉辅助定位、场景语义感知等   
原始图像数据带宽90MB/s, **仅限设备所在计算单元上使用, 切勿跨计算单元订阅**

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/sensor/rgb_head_rear/camera_info` | `CameraInfo` | 相机内参 | `RELIABLE`+`TRANSIENT_LOCAL` | N/A  
`/aima/hal/sensor/rgb_head_rear/rgb_image` | `Image` | 原始图像 | `TRANSIENT_LOCAL` | 10Hz  
`/aima/hal/sensor/rgb_head_rear/rgb_image/compressed` | `CompressedImage` | 压缩图像 | `TRANSIENT_LOCAL` | 10Hz  
  
注意: 后视RGB相机视野会被设在机器人后颈处的把手部分遮挡。 如所用算法受遮挡影响，可参照[头部后置单目相机数据订阅](/official/examples/cpp/camera-stream#cpp-echo-camera-head-rear)对图像进行mask预处理。

头部正位时后视RGB相机被遮挡情况如下:

<a id="id11"></a>

![后视RGB相机遮挡示意图](/official/_images/camera_head_rear_obstructed.jpg)

后视RGB相机遮挡示意图

<a id="id8"></a>

## 双目相机话题

双目相机位于开发计算单元(PC2), 可用于立体视觉、遥操、感知避障、目标识别、VIO SLAM、VLA等   
原始图像每路数据带宽90MB/s, **仅限设备所在计算单元上使用, 切勿跨计算单元订阅**

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/sensor/stereo_head_front_left/camera_info` | `CameraInfo` | 左目内参 | `RELIABLE`+`TRANSIENT_LOCAL` | N/A  
`/aima/hal/sensor/stereo_head_front_left/rgb_image` | `Image` | 左目原始图像 | `TRANSIENT_LOCAL` | 10Hz  
`/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed` | `CompressedImage` | 左目压缩图像 | `TRANSIENT_LOCAL` | 10Hz  
`/aima/hal/sensor/stereo_head_front_right/camera_info` | `CameraInfo` | 右目内参 | `RELIABLE`+`TRANSIENT_LOCAL` | N/A  
`/aima/hal/sensor/stereo_head_front_right/rgb_image` | `Image` | 右目原始图像 | `TRANSIENT_LOCAL` | 10Hz  
`/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed` | `CompressedImage` | 右目压缩图像 | `TRANSIENT_LOCAL` | 10Hz  
  
<a id="interface-rgbd-camera"></a>

## 深度相机话题

深度相机位于开发计算单元(PC2), 可用于目标检测、空间避障、环境语义获取等   
**原始图像数据每路带宽约25MB/s, 仅限设备所在计算单元上使用, 切勿跨计算单元订阅**

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/sensor/rgbd_head_front/rgb_camera_info` | `CameraInfo` | RGB内参 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/rgb_image` | `Image` | 原始图像 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/rgb_image/compressed` | `CompressedImage` | 压缩图像 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/depth_camera_info` | `CameraInfo` | 深度内参 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/depth_image` | `Image` | 深度图像 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/depth_pointcloud` | `PointCloud2` | 深度点云 | `RELIABLE` | 10Hz  
`/aima/hal/sensor/rgbd_head_front/imu` | `Imu` | IMU数据 | `RELIABLE` | 200Hz  
  
<a id="interface-lidar"></a>

## Lidar话题

提供Lidar点云数据和Lidar内置IMU数据, 可用于避障、建图定位等   
Lidar位于开发计算单元(PC2), 数据带宽10MB/s量级, **不建议** 跨计算单元订阅

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/sensor/lidar_chest_front/lidar_pointcloud` | `PointCloud2` | Lidar点云 | `TRANSIENT_LOCAL` | 10Hz  
`/aima/hal/sensor/lidar_chest_front/imu` | `Imu` | Lidar IMU数据 | `TRANSIENT_LOCAL` | 200Hz  
  
<a id="id9"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ：[代码示例](/official/examples/cpp/) 传感器接口部分

  * **Python 示例** ：[代码示例](/official/examples/python/) 传感器接口部分

<a id="id10"></a>

## 安全注意事项

注意

  * 数据带宽占用高的相机原始图像, 请勿跨计算单元订阅, 否则可能系统不稳定, 引发安全风险
