# 6.1.12 相机推流示例集

**该示例集提供了多种相机数据订阅和处理功能，支持深度相机、双目相机和单目相机的数据流订阅。**   
这些相机数据订阅 example 并没有实际的业务用途， 仅提供相机数据基础信息的打印；若您比较熟悉 ros2 使用，会发现 `ros2 topic echo` \+ `ros2 topic hz` 也能够实现 example 提供的功能。 您可以选择快速查阅 SDK 接口手册中话题列表直接快速进入自己模块的开发，也可以使用相机 example 作为脚手架加入自己的业务逻辑。 **我们发布的传感器数据均为未经预处理(去畸变等)的原始数据，如果您需要查询传感器的详细信息（如分辨率、焦距等），请关注相应的内参（camera_info）话题。**

<a id="py-echo-camera-rgbd"></a>

## 深度相机数据订阅

**该示例中用到了echo_camera_rgbd** ，通过订阅`/aima/hal/sensor/rgbd_head_front/`话题来接收机器人的深度相机数据，支持深度点云、深度图、RGB图、压缩RGB图和相机内参等多种数据类型。

**功能特点：**

  * 支持多种数据类型订阅（深度点云、深度图、RGB图、压缩图、相机内参）

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能(TBD, 请参考[C++示例](/official/examples/cpp/camera-stream#cpp-echo-camera-rgbd))

  * 可配置的topic类型选择

**支持的数据类型：**

  * `depth_pointcloud`: 深度点云数据 (sensor_msgs/PointCloud2)

  * `depth_image`: 深度图像 (sensor_msgs/Image)

  * `rgb_image`: RGB图像 (sensor_msgs/Image)

  * `rgb_image_compressed`: 压缩RGB图像 (sensor_msgs/CompressedImage)

  * `camera_info`: 相机内参 (sensor_msgs/CameraInfo)

```python
#!/usr/bin/env python3
"""
Head depth camera multi-topic subscription example

Supports selecting the topic type to subscribe via startup parameter --ros-args -p topic_type:=<type>:
  - depth_pointcloud: Depth point cloud (sensor_msgs/PointCloud2)
  - depth_image: Depth image (sensor_msgs/Image)
  - depth_camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)
  - rgb_image: RGB image (sensor_msgs/Image)
  - rgb_image_compressed: RGB compressed image (sensor_msgs/CompressedImage)
  - rgb_camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)

Example:
  ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=depth_pointcloud
  ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=rgb_image
  ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=rgb_camera_info

Default topic_type is rgb_image
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import Image, CompressedImage, CameraInfo, PointCloud2
from collections import deque
import time

class CameraTopicEcho(Node):
    def __init__(self):
        super().__init__('camera_topic_echo')

        # Select the topic type to subscribe
        self.declare_parameter('topic_type', 'rgb_image')
        self.declare_parameter('dump_video_path', '')

        self.topic_type = self.get_parameter('topic_type').value
        self.dump_video_path = self.get_parameter('dump_video_path').value

        # SensorDataQoS: BEST_EFFORT + VOLATILE
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5
        )

        # Create different subscribers based on topic_type
        if self.topic_type == "depth_pointcloud":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/depth_pointcloud"
            self.sub_pointcloud = self.create_subscription(
                PointCloud2, self.topic_name, self.cb_pointcloud, qos)
            self.get_logger().info(
                f"✅ Subscribing PointCloud2: {self.topic_name}")

        elif self.topic_type == "depth_image":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/depth_image"
            self.sub_image = self.create_subscription(
                Image, self.topic_name, self.cb_image, qos)
            self.get_logger().info(
                f"✅ Subscribing Depth Image: {self.topic_name}")

        elif self.topic_type == "rgb_image":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/rgb_image"
            self.sub_image = self.create_subscription(
                Image, self.topic_name, self.cb_image, qos)
            self.get_logger().info(
                f"✅ Subscribing RGB Image: {self.topic_name}")
            if self.dump_video_path:
                self.get_logger().info(
                    f"📝 Will dump received images to video: {self.dump_video_path}")

        elif self.topic_type == "rgb_image_compressed":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/rgb_image/compressed"
            self.sub_compressed = self.create_subscription(
                CompressedImage, self.topic_name, self.cb_compressed, qos)
            self.get_logger().info(
                f"✅ Subscribing CompressedImage: {self.topic_name}")

        elif self.topic_type == "rgb_camera_info":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/rgb_camera_info"
            # RGB-D CameraInfo is different with other cameras. The best_effort + volatile QoS is enough for 10Hz rgb_camera_info
            self.sub_camerainfo = self.create_subscription(
                CameraInfo, self.topic_name, self.cb_camerainfo, qos)
            self.get_logger().info(
                f"✅ Subscribing RGB CameraInfo: {self.topic_name}")

        elif self.topic_type == "depth_camera_info":
            self.topic_name = "/aima/hal/sensor/rgbd_head_front/depth_camera_info"
            # RGB-D CameraInfo is different with other cameras. The best_effort + volatile QoS is enough for 10Hz depth_camera_info
            self.sub_camerainfo = self.create_subscription(
                CameraInfo, self.topic_name, self.cb_camerainfo, qos)
            self.get_logger().info(
                f"✅ Subscribing Depth CameraInfo: {self.topic_name}")

        else:
            self.get_logger().error(f"Unknown topic_type: {self.topic_type}")
            raise ValueError("Unknown topic_type")

        # Internal state
        self.last_print = self.get_clock().now()
        self.print_allowed = False
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

    def should_print(self, master=True):
        """Control print frequency"""
        if not master:
            return self.print_allowed
        now = self.get_clock().now()
        if (now - self.last_print).nanoseconds * 1e-9 >= 1.0:
            self.last_print = now
            self.print_allowed = True
        else:
            self.print_allowed = False
        return self.print_allowed

    def cb_pointcloud(self, msg: PointCloud2):
        """PointCloud2 callback"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

            # Format fields information
            fields_str = " ".join(
                [f"{f.name}({f.datatype})" for f in msg.fields])

            self.get_logger().info(
                f"🌫️ PointCloud2 received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • width x height:  {msg.width} x {msg.height}\n"
                f"  • point_step:      {msg.point_step}\n"
                f"  • row_step:        {msg.row_step}\n"
                f"  • fields:          {fields_str}\n"
                f"  • is_bigendian:    {msg.is_bigendian}\n"
                f"  • is_dense:        {msg.is_dense}\n"
                f"  • data size:       {len(msg.data)}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

    def cb_image(self, msg: Image):
        """Image callback (Depth/RGB image)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"📸 {self.topic_type} received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • encoding:        {msg.encoding}\n"
                f"  • size (WxH):      {msg.width} x {msg.height}\n"
                f"  • step (bytes/row):{msg.step}\n"
                f"  • is_bigendian:    {msg.is_bigendian}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

        # Only RGB image supports video dump
        if self.topic_type == "rgb_image" and self.dump_video_path:
            self.dump_image_to_video(msg)

    def cb_compressed(self, msg: CompressedImage):
        """CompressedImage callback"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"🗜️  CompressedImage received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • format:          {msg.format}\n"
                f"  • data size:       {len(msg.data)}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

    def cb_camerainfo(self, msg: CameraInfo):
        """CameraInfo callback (camera intrinsic parameters)"""
        # Camera info will only receive one frame, print it directly
        stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # Format D array
        d_str = ", ".join([f"{d:.6f}" for d in msg.d])

        # Format K matrix
        k_str = ", ".join([f"{k:.6f}" for k in msg.k])

        # Format P matrix
        p_str = ", ".join([f"{p:.6f}" for p in msg.p])

        self.get_logger().info(
            f"📷 {self.topic_type} received\n"
            f"  • frame_id:        {msg.header.frame_id}\n"
            f"  • stamp (sec):     {stamp_sec:.6f}\n"
            f"  • width x height:  {msg.width} x {msg.height}\n"
            f"  • distortion_model:{msg.distortion_model}\n"
            f"  • D: [{d_str}]\n"
            f"  • K: [{k_str}]\n"
            f"  • P: [{p_str}]\n"
            f"  • binning_x: {msg.binning_x}\n"
            f"  • binning_y: {msg.binning_y}\n"
            f"  • roi: {{ x_offset: {msg.roi.x_offset}, y_offset: {msg.roi.y_offset}, height: {msg.roi.height}, width: {msg.roi.width}, do_rectify: {msg.roi.do_rectify} }}"
        )

    def dump_image_to_video(self, msg: Image):
        """Video dump is only supported for RGB images"""
        # You can add video recording functionality here
        # Simplified in the Python version, only logs instead
        if self.should_print(master=False):
            self.get_logger().info(f"📝 Video dump not implemented in Python version")

def main(args=None):
    rclpy.init(args=args)
    try:
        node = CameraTopicEcho()
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

  1. 订阅深度点云数据：

```bash
ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=depth_pointcloud
```

  2. 订阅RGB图像数据：

```bash
ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=rgb_image
```

  3. 订阅相机内参：

```bash
ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=rgb_camera_info
ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=depth_camera_info
```

  4. 录制RGB视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run py_examples echo_camera_rgbd --ros-args -p topic_type:=rgb_image -p dump_video_path:=$PWD/output.avi
```

<a id="py-echo-camera-stereo"></a>

## 双目相机数据订阅

**该示例中用到了echo_camera_stereo** ，通过订阅`/aima/hal/sensor/stereo_head_front_*/`话题来接收机器人的双目相机数据，支持左右相机的RGB图、压缩图和相机内参数据。

**功能特点：**

  * 支持左右相机独立数据订阅

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能(TBD, 请参考[C++示例](/official/examples/cpp/camera-stream#cpp-echo-camera-stereo))

  * 可配置的相机选择（左/右）

**支持的数据类型：**

  * `left_rgb_image`: 左相机RGB图像 (sensor_msgs/Image)

  * `left_rgb_image_compressed`: 左相机压缩RGB图像 (sensor_msgs/CompressedImage)

  * `left_camera_info`: 左相机内参 (sensor_msgs/CameraInfo)

  * `right_rgb_image`: 右相机RGB图像 (sensor_msgs/Image)

  * `right_rgb_image_compressed`: 右相机压缩RGB图像 (sensor_msgs/CompressedImage)

  * `right_camera_info`: 右相机内参 (sensor_msgs/CameraInfo)

```python
#!/usr/bin/env python3
"""
Head stereo camera multi-topic subscription example

Supports selecting the topic type to subscribe via startup parameter --ros-args -p topic_type:=<type>:
  - left_rgb_image: Left camera RGB image (sensor_msgs/Image)
  - left_rgb_image_compressed: Left camera RGB compressed image (sensor_msgs/CompressedImage)
  - left_camera_info: Left camera intrinsic parameters (sensor_msgs/CameraInfo)
  - right_rgb_image: Right camera RGB image (sensor_msgs/Image)
  - right_rgb_image_compressed: Right camera RGB compressed image (sensor_msgs/CompressedImage)
  - right_camera_info: Right camera intrinsic parameters (sensor_msgs/CameraInfo)

Example:
  ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=left_rgb_image
  ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=right_rgb_image
  ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=left_camera_info

Default topic_type is left_rgb_image
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import Image, CompressedImage, CameraInfo
from collections import deque
import time

class StereoCameraTopicEcho(Node):
    def __init__(self):
        super().__init__('stereo_camera_topic_echo')

        # Select the topic type to subscribe
        self.declare_parameter('topic_type', 'left_rgb_image')
        self.declare_parameter('dump_video_path', '')

        self.topic_type = self.get_parameter('topic_type').value
        self.dump_video_path = self.get_parameter('dump_video_path').value

        # Set QoS parameters - use sensor data QoS
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # Create different subscribers based on topic_type
        if self.topic_type == "left_rgb_image":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_left/rgb_image"
            self.sub_image = self.create_subscription(
                Image, self.topic_name, self.cb_image, qos)
            self.get_logger().info(
                f"✅ Subscribing Left RGB Image: {self.topic_name}")
            if self.dump_video_path:
                self.get_logger().info(
                    f"📝 Will dump received images to video: {self.dump_video_path}")

        elif self.topic_type == "left_rgb_image_compressed":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed"
            self.sub_compressed = self.create_subscription(
                CompressedImage, self.topic_name, self.cb_compressed, qos)
            self.get_logger().info(
                f"✅ Subscribing Left CompressedImage: {self.topic_name}")

        elif self.topic_type == "left_camera_info":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_left/camera_info"
            # CameraInfo subscription must use reliable + transient_local QoS to receive historical messages (even if only one frame is published)
            camera_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.RELIABLE,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=1,
                durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
            )
            self.sub_camerainfo = self.create_subscription(
                CameraInfo, self.topic_name, self.cb_camerainfo, camera_qos)
            self.get_logger().info(
                f"✅ Subscribing Left CameraInfo (with transient_local): {self.topic_name}")

        elif self.topic_type == "right_rgb_image":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_right/rgb_image"
            self.sub_image = self.create_subscription(
                Image, self.topic_name, self.cb_image, qos)
            self.get_logger().info(
                f"✅ Subscribing Right RGB Image: {self.topic_name}")
            if self.dump_video_path:
                self.get_logger().info(
                    f"📝 Will dump received images to video: {self.dump_video_path}")

        elif self.topic_type == "right_rgb_image_compressed":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed"
            self.sub_compressed = self.create_subscription(
                CompressedImage, self.topic_name, self.cb_compressed, qos)
            self.get_logger().info(
                f"✅ Subscribing Right CompressedImage: {self.topic_name}")

        elif self.topic_type == "right_camera_info":
            self.topic_name = "/aima/hal/sensor/stereo_head_front_right/camera_info"
            # CameraInfo subscription must use reliable + transient_local QoS to receive historical messages (even if only one frame is published)
            camera_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.RELIABLE,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=1,
                durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
            )
            self.sub_camerainfo = self.create_subscription(
                CameraInfo, self.topic_name, self.cb_camerainfo, camera_qos)
            self.get_logger().info(
                f"✅ Subscribing Right CameraInfo (with transient_local): {self.topic_name}")

        else:
            self.get_logger().error(f"Unknown topic_type: {self.topic_type}")
            raise ValueError("Unknown topic_type")

        # Internal state
        self.last_print = self.get_clock().now()
        self.print_allowed = False
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

    def should_print(self, master=True):
        """Control print frequency"""
        if not master:
            return self.print_allowed
        now = self.get_clock().now()
        if (now - self.last_print).nanoseconds * 1e-9 >= 1.0:
            self.last_print = now
            self.print_allowed = True
        else:
            self.print_allowed = False
        return self.print_allowed

    def cb_image(self, msg: Image):
        """Image callback (Left/Right camera RGB image)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"📸 {self.topic_type} received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • encoding:        {msg.encoding}\n"
                f"  • size (WxH):      {msg.width} x {msg.height}\n"
                f"  • step (bytes/row):{msg.step}\n"
                f"  • is_bigendian:    {msg.is_bigendian}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

        # Only RGB images support video dump
        if (self.topic_type in ["left_rgb_image", "right_rgb_image"]) and self.dump_video_path:
            self.dump_image_to_video(msg)

    def cb_compressed(self, msg: CompressedImage):
        """CompressedImage callback (Left/Right camera RGB compressed image)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"🗜️  {self.topic_type} received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • format:          {msg.format}\n"
                f"  • data size:       {len(msg.data)}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

    def cb_camerainfo(self, msg: CameraInfo):
        """CameraInfo callback (Left/Right camera intrinsic parameters)"""
        # Camera info will only receive one frame, print it directly
        stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # Format D array
        d_str = ", ".join([f"{d:.6f}" for d in msg.d])

        # Format K matrix
        k_str = ", ".join([f"{k:.6f}" for k in msg.k])

        # Format P matrix
        p_str = ", ".join([f"{p:.6f}" for p in msg.p])

        self.get_logger().info(
            f"📷 {self.topic_type} received\n"
            f"  • frame_id:        {msg.header.frame_id}\n"
            f"  • stamp (sec):     {stamp_sec:.6f}\n"
            f"  • width x height:  {msg.width} x {msg.height}\n"
            f"  • distortion_model:{msg.distortion_model}\n"
            f"  • D: [{d_str}]\n"
            f"  • K: [{k_str}]\n"
            f"  • P: [{p_str}]\n"
            f"  • binning_x: {msg.binning_x}\n"
            f"  • binning_y: {msg.binning_y}\n"
            f"  • roi: {{ x_offset: {msg.roi.x_offset}, y_offset: {msg.roi.y_offset}, height: {msg.roi.height}, width: {msg.roi.width}, do_rectify: {msg.roi.do_rectify} }}"
        )

    def dump_image_to_video(self, msg: Image):
        """Video dump is only supported for RGB images"""
        # You can add video recording functionality here
        # Simplified in the Python version, only logs instead
        if self.should_print(master=False):
            self.get_logger().info(f"📝 Video dump not implemented in Python version")

def main(args=None):
    rclpy.init(args=args)
    try:
        node = StereoCameraTopicEcho()
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

  1. 订阅左相机RGB图像：

```bash
ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=left_rgb_image
```

  2. 订阅右相机RGB图像：

```bash
ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=right_rgb_image
```

  3. 订阅左相机内参：

```bash
ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=left_camera_info
```

  4. 录制左相机视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run py_examples echo_camera_stereo --ros-args -p topic_type:=left_rgb_image -p dump_video_path:=$PWD/left_camera.avi
```

<a id="py-echo-camera-head-rear"></a>

## 头部后置单目相机数据订阅

**该示例中用到了echo_camera_head_rear** ，通过订阅`/aima/hal/sensor/rgb_head_rear/`话题来接收机器人的头部后置单目相机数据，支持RGB图、压缩图和相机内参数据。

**功能特点：**

  * 支持头部后置相机数据订阅

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能及把手遮挡区域mask处理(TBD, 请参考[C++示例](/official/examples/cpp/camera-stream#cpp-echo-camera-head-rear))

  * 可配置的topic类型选择

**支持的数据类型：**

  * `rgb_image`: RGB图像 (sensor_msgs/Image)

  * `rgb_image_compressed`: 压缩RGB图像 (sensor_msgs/CompressedImage)

  * `camera_info`: 相机内参 (sensor_msgs/CameraInfo)

```python
#!/usr/bin/env python3
"""
Head rear monocular camera multi-topic subscription example

Supports selecting the topic type to subscribe via startup parameter --ros-args -p topic_type:=<type>:
  - rgb_image: RGB image (sensor_msgs/Image)
  - rgb_image_compressed: RGB compressed image (sensor_msgs/CompressedImage)
  - camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)

Example:
  ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image
  ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image_compressed
  ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=camera_info

Default topic_type is rgb_image
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import Image, CompressedImage, CameraInfo
from collections import deque
import time
import os
import cv2

class HeadRearCameraTopicEcho(Node):
    def __init__(self):
        super().__init__('head_rear_camera_topic_echo')

        # Select the topic type to subscribe
        self.declare_parameter('topic_type', 'rgb_image')
        self.declare_parameter('dump_video_path', '')
        self.declare_parameter('with_mask', False)

        self.topic_type = self.get_parameter('topic_type').value
        self.dump_video_path = self.get_parameter('dump_video_path').value
        self.with_mask = self.get_parameter('with_mask').value
        self.mask_image = None

        # Set QoS parameters - use sensor data QoS
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        if self.with_mask and self.dump_video_path:
            mask_path = os.path.join(os.path.dirname(
                __file__), 'data', 'rgb_head_rear_mask.png')
            self.mask_image = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if self.mask_image is None:
                self.get_logger().error(
                    f"Failed to load mask file: {mask_path}")
                raise ValueError("Failed to load mask file")

        # Create different subscribers based on topic_type
        if self.topic_type == "rgb_image":
            self.topic_name = "/aima/hal/sensor/rgb_head_rear/rgb_image"
            self.sub_image = self.create_subscription(
                Image, self.topic_name, self.cb_image, qos)
            self.get_logger().info(
                f"✅ Subscribing RGB Image: {self.topic_name}")
            if self.dump_video_path:
                mask_state = "with mask" if self.with_mask else "without mask"
                self.get_logger().info(
                    f"📝 Will dump received images {mask_state} to video: {self.dump_video_path}")

        elif self.topic_type == "rgb_image_compressed":
            self.topic_name = "/aima/hal/sensor/rgb_head_rear/rgb_image/compressed"
            self.sub_compressed = self.create_subscription(
                CompressedImage, self.topic_name, self.cb_compressed, qos)
            self.get_logger().info(
                f"✅ Subscribing CompressedImage: {self.topic_name}")

        elif self.topic_type == "camera_info":
            self.topic_name = "/aima/hal/sensor/rgb_head_rear/camera_info"
            # CameraInfo subscription must use reliable + transient_local QoS to receive historical messages (even if only one frame is published)
            camera_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.RELIABLE,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=1,
                durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
            )
            self.sub_camerainfo = self.create_subscription(
                CameraInfo, self.topic_name, self.cb_camerainfo, camera_qos)
            self.get_logger().info(
                f"✅ Subscribing CameraInfo (with transient_local): {self.topic_name}")

        else:
            self.get_logger().error(f"Unknown topic_type: {self.topic_type}")
            raise ValueError("Unknown topic_type")

        # Internal state
        self.last_print = self.get_clock().now()
        self.print_allowed = False
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

    def should_print(self, master=True):
        """Control print frequency"""
        if not master:
            return self.print_allowed
        now = self.get_clock().now()
        if (now - self.last_print).nanoseconds * 1e-9 >= 1.0:
            self.last_print = now
            self.print_allowed = True
        else:
            self.print_allowed = False
        return self.print_allowed

    def cb_image(self, msg: Image):
        """Image callback (RGB image)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"📸 {self.topic_type} received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • encoding:        {msg.encoding}\n"
                f"  • size (WxH):      {msg.width} x {msg.height}\n"
                f"  • step (bytes/row):{msg.step}\n"
                f"  • is_bigendian:    {msg.is_bigendian}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

        # Only RGB image supports video dump
        if self.topic_type == "rgb_image" and self.dump_video_path:
            self.dump_image_to_video(msg)

    def cb_compressed(self, msg: CompressedImage):
        """CompressedImage callback (RGB compressed image)"""
        self.update_arrivals()

        if self.should_print():
            stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.get_logger().info(
                f"🗜️  {self.topic_type} received\n"
                f"  • frame_id:        {msg.header.frame_id}\n"
                f"  • stamp (sec):     {stamp_sec:.6f}\n"
                f"  • format:          {msg.format}\n"
                f"  • data size:       {len(msg.data)}\n"
                f"  • recv FPS (1s):   {self.get_fps():.1f}"
            )

    def cb_camerainfo(self, msg: CameraInfo):
        """CameraInfo callback (camera intrinsic parameters)"""
        # Camera info will only receive one frame, print it directly
        stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # Format D array
        d_str = ", ".join([f"{d:.6f}" for d in msg.d])

        # Format K matrix
        k_str = ", ".join([f"{k:.6f}" for k in msg.k])

        # Format P matrix
        p_str = ", ".join([f"{p:.6f}" for p in msg.p])

        self.get_logger().info(
            f"📷 {self.topic_type} received\n"
            f"  • frame_id:        {msg.header.frame_id}\n"
            f"  • stamp (sec):     {stamp_sec:.6f}\n"
            f"  • width x height:  {msg.width} x {msg.height}\n"
            f"  • distortion_model:{msg.distortion_model}\n"
            f"  • D: [{d_str}]\n"
            f"  • K: [{k_str}]\n"
            f"  • P: [{p_str}]\n"
            f"  • binning_x: {msg.binning_x}\n"
            f"  • binning_y: {msg.binning_y}\n"
            f"  • roi: {{ x_offset: {msg.roi.x_offset}, y_offset: {msg.roi.y_offset}, height: {msg.roi.height}, width: {msg.roi.width}, do_rectify: {msg.roi.do_rectify} }}"
        )

    def dump_image_to_video(self, msg: Image):
        """Video dump is only supported for RGB images"""
        # You can add video recording functionality here
        # Simplified in the Python version, only logs instead
        # Note: Refer to cpp implementation, get cv images by cv_bridge first,
        # then you can use 'image[self.mask_image == 0] = 0' to mask them and
        # finally use VideoWriter to save them as video
        if self.should_print(master=False):
            self.get_logger().info(f"📝 Video dump not implemented in Python version")

def main(args=None):
    rclpy.init(args=args)
    try:
        node = HeadRearCameraTopicEcho()
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

  1. 订阅RGB图像数据：

```bash
ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image
```

  2. 订阅压缩图像数据：

```bash
ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image_compressed
```

  3. 订阅相机内参：

```bash
ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=camera_info
```

  4. 录制视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run py_examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image -p dump_video_path:=$PWD/rear_camera.avi
```

**应用场景：**

  * 人脸识别和追踪

  * 目标检测和识别

  * 视觉SLAM

  * 图像处理和计算机视觉算法开发

  * 机器人视觉导航
