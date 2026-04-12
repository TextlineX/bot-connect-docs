# 6.2.12 相机推流示例集

**该示例集提供了多种相机数据订阅和处理功能，支持深度相机、双目相机和单目相机的数据流订阅。**   
这些相机数据订阅 example 并没有实际的业务用途， 仅提供相机数据基础信息的打印；若您比较熟悉 ros2 使用，会发现 `ros2 topic echo` \+ `ros2 topic hz` 也能够实现 example 提供的功能。 您可以选择快速查阅 SDK 接口手册中话题列表直接快速进入自己模块的开发，也可以使用相机 example 作为脚手架加入自己的业务逻辑。 **我们发布的传感器数据均为未经预处理(去畸变等)的原始数据，如果您需要查询传感器的详细信息（如分辨率、焦距等），请关注相应的内参（camera_info）话题。**

<a id="cpp-echo-camera-rgbd"></a>

## 深度相机数据订阅

**该示例中用到了echo_camera_rgbd** ，通过订阅`/aima/hal/sensor/rgbd_head_front/`话题来接收机器人的深度相机数据，支持深度点云、深度图、RGB图、压缩RGB图和相机内参等多种数据类型。

**功能特点：**

  * 支持多种数据类型订阅（深度点云、深度图、RGB图、压缩图、相机内参）

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能

  * 可配置的topic类型选择

**支持的数据类型：**

  * `depth_pointcloud`: 深度点云数据 (sensor_msgs/PointCloud2)

  * `depth_image`: 深度图像 (sensor_msgs/Image)

  * `rgb_image`: RGB图像 (sensor_msgs/Image)

  * `rgb_image_compressed`: 压缩RGB图像 (sensor_msgs/CompressedImage)

  * `camera_info`: 相机内参 (sensor_msgs/CameraInfo)

```cpp
#include <deque>
#include <iomanip>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/compressed_image.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sstream>
#include <string>
#include <vector>

// OpenCV headers for image/video writing
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

/**
 * @brief Example of subscribing to multiple topics for the head depth camera
 *
 * You can select which topic type to subscribe to via the startup argument
 * --ros-args -p topic_type:=<type>:
 *   - depth_pointcloud: Depth point cloud (sensor_msgs/PointCloud2)
 *   - depth_image: Depth image (sensor_msgs/Image)
 *   - rgb_image: RGB image (sensor_msgs/Image)
 *   - rgb_image_compressed: RGB compressed image (sensor_msgs/CompressedImage)
 *   - rgb_camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)
 *   - depth_camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)
 *
 * Examples:
 *   ros2 run examples echo_camera_rgbd --ros-args -p
 * topic_type:=depth_pointcloud ros2 run examples echo_camera_rgbd --ros-args -p
 * topic_type:=rgb_image ros2 run examples echo_camera_rgbd --ros-args -p
 * topic_type:=rgb_camera_info
 *
 * topic_type defaults to "rgb_image"
 *
 * See individual callbacks for more detailed comments
 */
class CameraTopicEcho : public rclcpp::Node {
public:
  CameraTopicEcho() : Node("camera_topic_echo") {
    // Select which topic type to subscribe to
    topic_type_ = declare_parameter<std::string>("topic_type", "rgb_image");
    dump_video_path_ = declare_parameter<std::string>("dump_video_path", "");

    // Subscribed topics and their message layouts
    // 1. /aima/hal/sensor/rgbd_head_front/depth_pointcloud
    //    - topic_type: depth_pointcloud
    //    - message type: sensor_msgs::msg::PointCloud2
    //    - frame_id: rgbd_head_front
    //    - child_frame_id: /
    //    - contents: depth point cloud
    // 2. /aima/hal/sensor/rgbd_head_front/depth_image
    //    - topic_type: depth_image
    //    - message type: sensor_msgs::msg::Image
    //    - frame_id: rgbd_head_front
    //    - contents: depth image
    // 3. /aima/hal/sensor/rgbd_head_front/rgb_image
    //    - topic_type: rgb_image
    //    - message type: sensor_msgs::msg::Image
    //    - frame_id: rgbd_head_front
    //    - contents: RGB image
    // 4. /aima/hal/sensor/rgbd_head_front/rgb_image/compressed
    //    - topic_type: rgb_image_compressed
    //    - message type: sensor_msgs::msg::CompressedImage
    //    - frame_id: rgbd_head_front
    //    - contents: RGB compressed image
    // 5. /aima/hal/sensor/rgbd_head_front/rgb_camera_info
    //    - topic_type: camera_info
    //    - message type: sensor_msgs::msg::CameraInfo
    //    - frame_id: rgbd_head_front
    //    - contents: RGB camera intrinsic parameters
    // 6. /aima/hal/sensor/rgbd_head_front/depth_camera_info
    //    - topic_type: camera_info
    //    - message type: sensor_msgs::msg::CameraInfo
    //    - frame_id: rgbd_head_front
    //    - contents: RGB camera intrinsic parameters

    auto qos = rclcpp::SensorDataQoS();

    // Enable depth pointcloud subscription
    if (topic_type_ == "depth_pointcloud") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/depth_pointcloud";
      sub_pointcloud_ = create_subscription<sensor_msgs::msg::PointCloud2>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_pointcloud, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing PointCloud2: %s",
                  topic_name_.c_str());

      // Enable depth image subscription
    } else if (topic_type_ == "depth_image") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/depth_image";
      sub_image_ = create_subscription<sensor_msgs::msg::Image>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_image, this, std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Depth Image: %s",
                  topic_name_.c_str());

      // Enable RGB image subscription
    } else if (topic_type_ == "rgb_image") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/rgb_image";
      sub_image_ = create_subscription<sensor_msgs::msg::Image>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_image, this, std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing RGB Image: %s",
                  topic_name_.c_str());
      if (!dump_video_path_.empty()) {
        RCLCPP_INFO(get_logger(), "📝 Will dump received images to video: %s",
                    dump_video_path_.c_str());
      }

      // Enable RGB compressed image subscription
    } else if (topic_type_ == "rgb_image_compressed") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/rgb_image/compressed";
      sub_compressed_ = create_subscription<sensor_msgs::msg::CompressedImage>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_compressed, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing CompressedImage: %s",
                  topic_name_.c_str());

      // Enable rgb camera info subscription
    } else if (topic_type_ == "rgb_camera_info") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/rgb_camera_info";
      // RGB-D CameraInfo subscriptions is different with other cameras.
      // The messages arrive in about 10Hz and SensorDataQoS is enough.
      sub_camerainfo_ = create_subscription<sensor_msgs::msg::CameraInfo>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_camerainfo, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing RGB CameraInfo: %s",
                  topic_name_.c_str());

      // Enable depth camera info subscription
    } else if (topic_type_ == "depth_camera_info") {
      topic_name_ = "/aima/hal/sensor/rgbd_head_front/depth_camera_info";
      // RGB-D CameraInfo subscriptions is different with other cameras.
      // The messages arrive in about 10Hz and SensorDataQoS is enough.
      sub_camerainfo_ = create_subscription<sensor_msgs::msg::CameraInfo>(
          topic_name_, qos,
          std::bind(&CameraTopicEcho::cb_camerainfo, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Depth CameraInfo: %s",
                  topic_name_.c_str());

      // Unknown topic_type error
    } else {
      RCLCPP_ERROR(get_logger(), "Unknown topic_type: %s", topic_type_.c_str());
      throw std::runtime_error("Unknown topic_type");
    }
  }

  ~CameraTopicEcho() override {
    if (video_writer_.isOpened()) {
      video_writer_.release();
      RCLCPP_INFO(get_logger(), "Video file closed.");
    }
  }

private:
  // PointCloud2 callback
  void cb_pointcloud(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    // Update arrivals (for FPS calculation)
    update_arrivals();

    // Print point cloud basic info
    if (should_print()) {
      std::ostringstream oss;
      oss << "🌫️ PointCloud2 received\n"
          << "  • frame_id:        " << msg->header.frame_id << "\n"
          << "  • stamp (sec):     "
          << rclcpp::Time(msg->header.stamp).seconds() << "\n"
          << "  • width x height:  " << msg->width << " x " << msg->height
          << "\n"
          << "  • point_step:      " << msg->point_step << "\n"
          << "  • row_step:        " << msg->row_step << "\n"
          << "  • fields:          ";
      for (const auto &f : msg->fields)
        oss << f.name << "(" << (int)f.datatype << ") ";
      oss << "\n  • is_bigendian:    " << msg->is_bigendian
          << "\n  • is_dense:        " << msg->is_dense
          << "\n  • data size:       " << msg->data.size()
          << "\n  • recv FPS (1s):   " << get_fps();
      RCLCPP_INFO(get_logger(), "%s", oss.str().c_str());
    }
  }

  // Image callback (depth/RGB image)
  void cb_image(const sensor_msgs::msg::Image::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "📸 %s received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • encoding:        %s\n"
                  "  • size (WxH):      %u x %u\n"
                  "  • step (bytes/row):%u\n"
                  "  • is_bigendian:    %u\n"
                  "  • recv FPS (1s):   %.1f",
                  topic_type_.c_str(), msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->encoding.c_str(), msg->width, msg->height, msg->step,
                  msg->is_bigendian, get_fps());
    }

    // Video dump is supported only for RGB images
    if (topic_type_ == "rgb_image" && !dump_video_path_.empty()) {
      dump_image_to_video(msg);
    }
  }

  // CompressedImage callback
  void cb_compressed(const sensor_msgs::msg::CompressedImage::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "🗜️  CompressedImage received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • format:          %s\n"
                  "  • data size:       %zu\n"
                  "  • recv FPS (1s):   %.1f",
                  msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->format.c_str(), msg->data.size(), get_fps());
    }
  }

  // CameraInfo callback (camera intrinsic parameters)
  void cb_camerainfo(const sensor_msgs::msg::CameraInfo::SharedPtr msg) {
    // CameraInfo is typically published once; print it once
    std::ostringstream oss;
    oss << "📷 " << topic_type_ << " received\n"
        << "  • frame_id:        " << msg->header.frame_id << "\n"
        << "  • stamp (sec):     " << rclcpp::Time(msg->header.stamp).seconds()
        << "\n"
        << "  • width x height:  " << msg->width << " x " << msg->height << "\n"
        << "  • distortion_model:" << msg->distortion_model << "\n"
        << "  • D: [";
    for (size_t i = 0; i < msg->d.size(); ++i) {
      oss << msg->d[i];
      if (i + 1 < msg->d.size())
        oss << ", ";
    }
    oss << "]\n  • K: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->k[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • R: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->r[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • P: [";
    for (int i = 0; i < 12; ++i) {
      oss << msg->p[i];
      if (i + 1 < 12)
        oss << ", ";
    }
    oss << "]\n"
        << "  • binning_x: " << msg->binning_x << "\n"
        << "  • binning_y: " << msg->binning_y << "\n"
        << "  • roi: { x_offset: " << msg->roi.x_offset
        << ", y_offset: " << msg->roi.y_offset
        << ", height: " << msg->roi.height << ", width: " << msg->roi.width
        << ", do_rectify: " << (msg->roi.do_rectify ? "true" : "false") << " }";
    RCLCPP_INFO(get_logger(), "%s", oss.str().c_str());
  }

  // Track arrival timestamps to compute FPS
  void update_arrivals() {
    const rclcpp::Time now = this->get_clock()->now();
    arrivals_.push_back(now);
    while (!arrivals_.empty() && (now - arrivals_.front()).seconds() > 1.0) {
      arrivals_.pop_front();
    }
  }
  double get_fps() const { return static_cast<double>(arrivals_.size()); }

  // Control printing frequency
  bool should_print() {
    const rclcpp::Time now = this->get_clock()->now();
    if ((now - last_print_).seconds() >= 1.0) {
      last_print_ = now;
      return true;
    }
    return false;
  }

  // Dump received images to a video file (RGB images only)
  void dump_image_to_video(const sensor_msgs::msg::Image::SharedPtr &msg) {
    cv::Mat image;
    try {
      // Obtain the Mat without copying by not specifying encoding
      cv_bridge::CvImageConstPtr cvp = cv_bridge::toCvShare(msg);
      image = cvp->image;
      // Convert to BGR for uniform saving
      if (msg->encoding == "rgb8") {
        cv::cvtColor(image, image, cv::COLOR_RGB2BGR);
      } else {
        RCLCPP_WARN(get_logger(), "image encoding not expected: %s",
                    msg->encoding.c_str());
        return;
      }
    } catch (const std::exception &e) {
      RCLCPP_WARN(get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }

    // Initialize VideoWriter
    if (!video_writer_.isOpened()) {
      int fourcc = cv::VideoWriter::fourcc('M', 'J', 'P', 'G');
      double fps = std::max(1.0, get_fps());
      bool ok = video_writer_.open(dump_video_path_, fourcc, fps,
                                   cv::Size(image.cols, image.rows), true);
      if (!ok) {
        RCLCPP_ERROR(get_logger(), "Failed to open video file: %s",
                     dump_video_path_.c_str());
        dump_video_path_.clear(); // stop trying
        return;
      }
      RCLCPP_INFO(get_logger(), "VideoWriter started: %s, size=%dx%d, fps=%.1f",
                  dump_video_path_.c_str(), image.cols, image.rows, fps);
    }
    video_writer_.write(image);
  }

  // Member variables
  std::string topic_type_;
  std::string topic_name_;
  std::string dump_video_path_;

  // Subscriptions
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_image_;
  rclcpp::Subscription<sensor_msgs::msg::CompressedImage>::SharedPtr
      sub_compressed_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr sub_camerainfo_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr
      sub_pointcloud_;

  // FPS statistics
  rclcpp::Time last_print_{0, 0, RCL_ROS_TIME};
  std::deque<rclcpp::Time> arrivals_;

  // Video writer
  cv::VideoWriter video_writer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<CameraTopicEcho>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

**使用说明：**

  1. 订阅深度点云数据：

```bash
ros2 run examples echo_camera_rgbd --ros-args -p topic_type:=depth_pointcloud
```

  2. 订阅RGB图像数据：

```bash
ros2 run examples echo_camera_rgbd --ros-args -p topic_type:=rgb_image
```

  3. 订阅相机内参：

```bash
ros2 run examples echo_camera_rgbd --ros-args -p topic_type:=rgb_camera_info
ros2 run examples echo_camera_rgbd --ros-args -p topic_type:=depth_camera_info
```

  4. 录制RGB视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run examples echo_camera_rgbd --ros-args -p topic_type:=rgb_image -p dump_video_path:=$PWD/output.avi
```

<a id="cpp-echo-camera-stereo"></a>

## 双目相机数据订阅

**该示例中用到了echo_camera_stereo** ，通过订阅`/aima/hal/sensor/stereo_head_front_*/`话题来接收机器人的双目相机数据，支持左右相机的RGB图、压缩图和相机内参数据。

**功能特点：**

  * 支持左右相机独立数据订阅

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能

  * 可配置的相机选择（左/右）

**支持的数据类型：**

  * `left_rgb_image`: 左相机RGB图像 (sensor_msgs/Image)

  * `left_rgb_image_compressed`: 左相机压缩RGB图像 (sensor_msgs/CompressedImage)

  * `left_camera_info`: 左相机内参 (sensor_msgs/CameraInfo)

  * `right_rgb_image`: 右相机RGB图像 (sensor_msgs/Image)

  * `right_rgb_image_compressed`: 右相机压缩RGB图像 (sensor_msgs/CompressedImage)

  * `right_camera_info`: 右相机内参 (sensor_msgs/CameraInfo)

```cpp
#include <deque>
#include <iomanip>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/compressed_image.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sstream>
#include <string>
#include <vector>

// OpenCV headers for image/video writing
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

/**
 * @brief Example of subscribing to multiple topics for the stereo head camera
 *
 * You can select which topic type to subscribe to via the startup argument
 * --ros-args -p topic_type:=<type>:
 *   - left_rgb_image: left camera RGB image (sensor_msgs/Image)
 *   - left_rgb_image_compressed: left camera RGB compressed image
 * (sensor_msgs/CompressedImage)
 *   - left_camera_info: left camera intrinsic parameters
 * (sensor_msgs/CameraInfo)
 *   - right_rgb_image: right camera RGB image (sensor_msgs/Image)
 *   - right_rgb_image_compressed: right camera RGB compressed image
 * (sensor_msgs/CompressedImage)
 *   - right_camera_info: right camera intrinsic parameters
 * (sensor_msgs/CameraInfo)
 *
 * Examples:
 *   ros2 run examples echo_camera_stereo --ros-args -p
 * topic_type:=left_rgb_image ros2 run examples echo_camera_stereo --ros-args -p
 * topic_type:=right_rgb_image ros2 run examples echo_camera_stereo --ros-args
 * -p topic_type:=left_camera_info
 *
 * topic_type defaults to "left_rgb_image"
 *
 * See individual callbacks for more detailed comments
 */
class StereoCameraTopicEcho : public rclcpp::Node {
public:
  StereoCameraTopicEcho() : Node("stereo_camera_topic_echo") {
    // Select which topic type to subscribe to
    topic_type_ =
        declare_parameter<std::string>("topic_type", "left_rgb_image");
    dump_video_path_ = declare_parameter<std::string>("dump_video_path", "");

    // Subscribed topics and their message layouts
    // 1. /aima/hal/sensor/stereo_head_front_left/rgb_image
    //    - topic_type: left_rgb_image
    //    - message type: sensor_msgs::msg::Image
    //    - frame_id: stereo_head_front
    //    - child_frame_id: /
    //    - contents: left camera raw image
    // 2. /aima/hal/sensor/stereo_head_front_left/rgb_image/compressed
    //    - topic_type: left_rgb_image_compressed
    //    - message type: sensor_msgs::msg::CompressedImage
    //    - frame_id: stereo_head_front
    //    - contents: left camera compressed image
    // 3. /aima/hal/sensor/stereo_head_front_left/camera_info
    //    - topic_type: left_camera_info
    //    - message type: sensor_msgs::msg::CameraInfo
    //    - frame_id: stereo_head_front
    //    - contents: left camera intrinsic parameters
    // 4. /aima/hal/sensor/stereo_head_front_right/rgb_image
    //    - topic_type: right_rgb_image
    //    - message type: sensor_msgs::msg::Image
    //    - frame_id: stereo_head_front_right
    //    - child_frame_id: /
    //    - contents: right camera raw image
    // 5. /aima/hal/sensor/stereo_head_front_right/rgb_image/compressed
    //    - topic_type: right_rgb_image_compressed
    //    - message type: sensor_msgs::msg::CompressedImage
    //    - frame_id: stereo_head_front_right
    //    - contents: right camera compressed image
    // 6. /aima/hal/sensor/stereo_head_front_right/camera_info
    //    - topic_type: right_camera_info
    //    - message type: sensor_msgs::msg::CameraInfo
    //    - frame_id: stereo_head_front_right
    //    - contents: right camera intrinsic parameters

    // Set QoS parameters - use SensorData QoS
    auto qos = rclcpp::SensorDataQoS();

    // Enable left camera RGB image subscription
    if (topic_type_ == "left_rgb_image") {
      topic_name_ = "/aima/hal/sensor/stereo_head_front_left/rgb_image";
      sub_image_ = create_subscription<sensor_msgs::msg::Image>(
          topic_name_, qos,
          std::bind(&StereoCameraTopicEcho::cb_image, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Left RGB Image: %s",
                  topic_name_.c_str());
      if (!dump_video_path_.empty()) {
        RCLCPP_INFO(get_logger(), "📝 Will dump received images to video: %s",
                    dump_video_path_.c_str());
      }

      // Enable left camera RGB compressed image subscription
    } else if (topic_type_ == "left_rgb_image_compressed") {
      topic_name_ =
          "/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed";
      sub_compressed_ = create_subscription<sensor_msgs::msg::CompressedImage>(
          topic_name_, qos,
          std::bind(&StereoCameraTopicEcho::cb_compressed, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Left CompressedImage: %s",
                  topic_name_.c_str());

      // Enable left camera info subscription
    } else if (topic_type_ == "left_camera_info") {

      topic_name_ = "/aima/hal/sensor/stereo_head_front_left/camera_info";
      // CameraInfo subscriptions must use reliable + transient_local
      // QoS in order to receive latched/history messages (even if only one
      // message was published). Here we use keep_last(1) + reliable
      // + transient_local.
      sub_camerainfo_ = create_subscription<sensor_msgs::msg::CameraInfo>(
          topic_name_,
          rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local(),
          std::bind(&StereoCameraTopicEcho::cb_camerainfo, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(),
                  "✅ Subscribing Left CameraInfo (with transient_local): %s",
                  topic_name_.c_str());

      // Enable right camera RGB image subscription
    } else if (topic_type_ == "right_rgb_image") {
      topic_name_ = "/aima/hal/sensor/stereo_head_front_right/rgb_image";
      sub_image_ = create_subscription<sensor_msgs::msg::Image>(
          topic_name_, qos,
          std::bind(&StereoCameraTopicEcho::cb_image, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Right RGB Image: %s",
                  topic_name_.c_str());
      if (!dump_video_path_.empty()) {
        RCLCPP_INFO(get_logger(), "📝 Will dump received images to video: %s",
                    dump_video_path_.c_str());
      }

      // Enable right camera RGB compressed image subscription
    } else if (topic_type_ == "right_rgb_image_compressed") {
      topic_name_ =
          "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed";
      sub_compressed_ = create_subscription<sensor_msgs::msg::CompressedImage>(
          topic_name_, qos,
          std::bind(&StereoCameraTopicEcho::cb_compressed, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing Right CompressedImage: %s",
                  topic_name_.c_str());

      // Enable right camera info subscription
    } else if (topic_type_ == "right_camera_info") {
      topic_name_ = "/aima/hal/sensor/stereo_head_front_right/camera_info";
      // CameraInfo subscriptions must use reliable + transient_local
      // QoS in order to receive latched/history messages (even if only one
      // message was published). Here we use keep_last(1) + reliable
      // + transient_local.
      sub_camerainfo_ = create_subscription<sensor_msgs::msg::CameraInfo>(
          topic_name_,
          rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local(),
          std::bind(&StereoCameraTopicEcho::cb_camerainfo, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(),
                  "✅ Subscribing Right CameraInfo (with transient_local): %s",
                  topic_name_.c_str());

      // Unknown topic_type error
    } else {
      RCLCPP_ERROR(get_logger(), "Unknown topic_type: %s", topic_type_.c_str());
      throw std::runtime_error("Unknown topic_type");
    }
  }

  ~StereoCameraTopicEcho() override {
    if (video_writer_.isOpened()) {
      video_writer_.release();
      RCLCPP_INFO(get_logger(), "Video file closed.");
    }
  }

private:
  // Image callback (left/right RGB image)
  void cb_image(const sensor_msgs::msg::Image::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "📸 %s received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • encoding:        %s\n"
                  "  • size (WxH):      %u x %u\n"
                  "  • step (bytes/row):%u\n"
                  "  • is_bigendian:    %u\n"
                  "  • recv FPS (1s):   %.1f",
                  topic_type_.c_str(), msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->encoding.c_str(), msg->width, msg->height, msg->step,
                  msg->is_bigendian, get_fps());
    }

    // Video dump is supported only for RGB images
    if ((topic_type_ == "left_rgb_image" || topic_type_ == "right_rgb_image") &&
        !dump_video_path_.empty()) {
      dump_image_to_video(msg);
    }
  }

  // CompressedImage callback (left/right RGB compressed image)
  void cb_compressed(const sensor_msgs::msg::CompressedImage::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "🗜️  %s received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • format:          %s\n"
                  "  • data size:       %zu\n"
                  "  • recv FPS (1s):   %.1f",
                  topic_type_.c_str(), msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->format.c_str(), msg->data.size(), get_fps());
    }
  }

  // CameraInfo callback (left/right camera intrinsic parameters)
  void cb_camerainfo(const sensor_msgs::msg::CameraInfo::SharedPtr msg) {
    // CameraInfo is typically published once; print it once
    std::ostringstream oss;
    oss << "📷 " << topic_type_ << " received\n"
        << "  • frame_id:        " << msg->header.frame_id << "\n"
        << "  • stamp (sec):     " << rclcpp::Time(msg->header.stamp).seconds()
        << "\n"
        << "  • width x height:  " << msg->width << " x " << msg->height << "\n"
        << "  • distortion_model:" << msg->distortion_model << "\n"
        << "  • D: [";
    for (size_t i = 0; i < msg->d.size(); ++i) {
      oss << msg->d[i];
      if (i + 1 < msg->d.size())
        oss << ", ";
    }
    oss << "]\n  • K: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->k[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • R: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->r[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • P: [";
    for (int i = 0; i < 12; ++i) {
      oss << msg->p[i];
      if (i + 1 < 12)
        oss << ", ";
    }
    oss << "]\n"
        << "  • binning_x: " << msg->binning_x << "\n"
        << "  • binning_y: " << msg->binning_y << "\n"
        << "  • roi: { x_offset: " << msg->roi.x_offset
        << ", y_offset: " << msg->roi.y_offset
        << ", height: " << msg->roi.height << ", width: " << msg->roi.width
        << ", do_rectify: " << (msg->roi.do_rectify ? "true" : "false") << " }";
    RCLCPP_INFO(get_logger(), "%s", oss.str().c_str());
  }

  // Track arrival timestamps to compute FPS
  void update_arrivals() {
    const rclcpp::Time now = this->get_clock()->now();
    arrivals_.push_back(now);
    while (!arrivals_.empty() && (now - arrivals_.front()).seconds() > 1.0) {
      arrivals_.pop_front();
    }
  }
  double get_fps() const { return static_cast<double>(arrivals_.size()); }

  // Control printing frequency
  bool should_print() {
    const rclcpp::Time now = this->get_clock()->now();
    if ((now - last_print_).seconds() >= 1.0) {
      last_print_ = now;
      return true;
    }
    return false;
  }

  // Dump received images to a video file (RGB images only)
  void dump_image_to_video(const sensor_msgs::msg::Image::SharedPtr &msg) {
    cv::Mat image;
    try {
      // Obtain the Mat without copying by not specifying encoding
      cv_bridge::CvImageConstPtr cvp = cv_bridge::toCvShare(msg);
      image = cvp->image;
      // Convert to BGR for uniform saving
      if (msg->encoding == "rgb8") {
        cv::cvtColor(image, image, cv::COLOR_RGB2BGR);
      } else {
        RCLCPP_WARN(get_logger(), "image encoding not expected: %s",
                    msg->encoding.c_str());
        return;
      }
    } catch (const std::exception &e) {
      RCLCPP_WARN(get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }

    // Initialize VideoWriter
    if (!video_writer_.isOpened()) {
      int fourcc = cv::VideoWriter::fourcc('M', 'J', 'P', 'G');
      double fps = std::max(1.0, get_fps());
      bool ok = video_writer_.open(dump_video_path_, fourcc, fps,
                                   cv::Size(image.cols, image.rows), true);
      if (!ok) {
        RCLCPP_ERROR(get_logger(), "Failed to open video file: %s",
                     dump_video_path_.c_str());
        dump_video_path_.clear(); // stop trying
        return;
      }
      RCLCPP_INFO(get_logger(), "VideoWriter started: %s, size=%dx%d, fps=%.1f",
                  dump_video_path_.c_str(), image.cols, image.rows, fps);
    }
    video_writer_.write(image);
  }

  // Member variables
  std::string topic_type_;
  std::string topic_name_;
  std::string dump_video_path_;

  // Subscriptions
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_image_;
  rclcpp::Subscription<sensor_msgs::msg::CompressedImage>::SharedPtr
      sub_compressed_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr sub_camerainfo_;

  // FPS statistics
  rclcpp::Time last_print_{0, 0, RCL_ROS_TIME};
  std::deque<rclcpp::Time> arrivals_;

  // Video writer
  cv::VideoWriter video_writer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<StereoCameraTopicEcho>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

**使用说明：**

  1. 订阅左相机RGB图像：

```bash
ros2 run examples echo_camera_stereo --ros-args -p topic_type:=left_rgb_image
```

  2. 订阅右相机RGB图像：

```bash
ros2 run examples echo_camera_stereo --ros-args -p topic_type:=right_rgb_image
```

  3. 订阅左相机内参：

```bash
ros2 run examples echo_camera_stereo --ros-args -p topic_type:=left_camera_info
```

  4. 录制左相机视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run examples echo_camera_stereo --ros-args -p topic_type:=left_rgb_image -p dump_video_path:=$PWD/left_camera.avi
```

<a id="cpp-echo-camera-head-rear"></a>

## 头部后置单目相机数据订阅

**该示例中用到了echo_camera_head_rear** ，通过订阅`/aima/hal/sensor/rgb_head_rear/`话题来接收机器人的头部后置单目相机数据，支持RGB图(及其mask处理)、压缩图和相机内参数据。

**功能特点：**

  * 支持头部后置相机数据订阅

  * 实时FPS统计和数据显示

  * 支持RGB图视频录制功能及把手遮挡区域mask处理

  * 可配置的topic类型选择

**支持的数据类型：**

  * `rgb_image`: RGB图像 (sensor_msgs/Image)

  * `rgb_image_compressed`: 压缩RGB图像 (sensor_msgs/CompressedImage)

  * `camera_info`: 相机内参 (sensor_msgs/CameraInfo)

```cpp
#include <deque>
#include <filesystem>
#include <iomanip>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/compressed_image.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sstream>
#include <string>
#include <vector>

// OpenCV headers for image/video writing
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

/**
 * @brief Example of subscribing to multiple topics for the rear head monocular
 * camera
 *
 * You can select which topic type to subscribe to via the startup argument
 * --ros-args -p topic_type:=<type>:
 *   - rgb_image: RGB image (sensor_msgs/Image)
 *   - rgb_image_compressed: RGB compressed image (sensor_msgs/CompressedImage)
 *   - camera_info: Camera intrinsic parameters (sensor_msgs/CameraInfo)
 *
 * Examples:
 *   ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image
 *   ros2 run examples echo_camera_head_rear --ros-args -p
 * topic_type:=rgb_image_compressed ros2 run examples echo_camera_head_rear
 * --ros-args -p topic_type:=camera_info
 *
 * topic_type defaults to "rgb_image"
 *
 * See individual callbacks for more detailed comments
 */
class HeadRearCameraTopicEcho : public rclcpp::Node {
public:
  HeadRearCameraTopicEcho() : Node("head_rear_camera_topic_echo") {
    // Select which topic type to subscribe to
    topic_type_ = declare_parameter<std::string>("topic_type", "rgb_image");
    dump_video_path_ = declare_parameter<std::string>("dump_video_path", "");
    with_mask_ = declare_parameter<bool>("with_mask", false);

    // Subscribed topics and their message layouts
    // 1. /aima/hal/sensor/rgb_head_rear/rgb_image
    //    - topic_type: rgb_image
    //    - message type: sensor_msgs::msg::Image
    //    - frame_id: rgb_head_rear
    //    - child_frame_id: /
    //    - contents: raw image data
    // 2. /aima/hal/sensor/rgb_head_rear/rgb_image/compressed
    //    - topic_type: rgb_image_compressed
    //    - message type: sensor_msgs::msg::CompressedImage
    //    - frame_id: rgb_head_rear
    //    - contents: compressed image data
    // 3. /aima/hal/sensor/rgb_head_rear/camera_info
    //    - topic_type: camera_info
    //    - message type: sensor_msgs::msg::CameraInfo
    //    - frame_id: rgb_head_rear
    //    - contents: camera intrinsic parameters

    // Set QoS parameters - use SensorData QoS
    auto qos = rclcpp::SensorDataQoS();

    if (with_mask_ && !dump_video_path_.empty()) {
      auto mask_path =
          std::filesystem::read_symlink("/proc/self/exe").parent_path() /
          "data" / "rgb_head_rear_mask.png";
      mask_image_ = cv::imread(mask_path, cv::IMREAD_GRAYSCALE);
      if (mask_image_.empty()) {
        RCLCPP_ERROR(get_logger(), "Failed to load mask file from %s",
                     mask_path.c_str());
        throw std::runtime_error("Failed to load mask file");
      }
    }

    // Enable RGB image subscription
    if (topic_type_ == "rgb_image") {
      topic_name_ = "/aima/hal/sensor/rgb_head_rear/rgb_image";
      sub_image_ = create_subscription<sensor_msgs::msg::Image>(
          topic_name_, qos,
          std::bind(&HeadRearCameraTopicEcho::cb_image, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing RGB Image: %s",
                  topic_name_.c_str());
      if (!dump_video_path_.empty()) {
        RCLCPP_INFO(
            get_logger(), "📝 Will dump received images %s mask to video: %s",
            (with_mask_ ? "with" : "without"), dump_video_path_.c_str());
      }
    }

    // Enable RGB compressed image subscription
    else if (topic_type_ == "rgb_image_compressed") {
      topic_name_ = "/aima/hal/sensor/rgb_head_rear/rgb_image/compressed";
      sub_compressed_ = create_subscription<sensor_msgs::msg::CompressedImage>(
          topic_name_, qos,
          std::bind(&HeadRearCameraTopicEcho::cb_compressed, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(), "✅ Subscribing CompressedImage: %s",
                  topic_name_.c_str());

      // Enable camera info subscription
    } else if (topic_type_ == "camera_info") {
      topic_name_ = "/aima/hal/sensor/rgb_head_rear/camera_info";
      // CameraInfo subscriptions must use reliable + transient_local
      // QoS in order to receive latched/history messages (even if only one
      // message was published). Here we use keep_last(1) + reliable
      // + transient_local.
      sub_camerainfo_ = create_subscription<sensor_msgs::msg::CameraInfo>(
          topic_name_,
          rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local(),
          std::bind(&HeadRearCameraTopicEcho::cb_camerainfo, this,
                    std::placeholders::_1));
      RCLCPP_INFO(get_logger(),
                  "✅ Subscribing CameraInfo (with transient_local): %s",
                  topic_name_.c_str());

      // Unknown topic_type error
    } else {
      RCLCPP_ERROR(get_logger(), "Unknown topic_type: %s", topic_type_.c_str());
      throw std::runtime_error("Unknown topic_type");
    }
  }

  ~HeadRearCameraTopicEcho() override {
    if (video_writer_.isOpened()) {
      video_writer_.release();
      RCLCPP_INFO(get_logger(), "Video file closed.");
    }
  }

private:
  // Image callback (RGB image)
  void cb_image(const sensor_msgs::msg::Image::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "📸 %s received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • encoding:        %s\n"
                  "  • size (WxH):      %u x %u\n"
                  "  • step (bytes/row):%u\n"
                  "  • is_bigendian:    %u\n"
                  "  • recv FPS (1s):   %.1f",
                  topic_type_.c_str(), msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->encoding.c_str(), msg->width, msg->height, msg->step,
                  msg->is_bigendian, get_fps());
    }

    // Video dump is supported only for RGB images
    if (topic_type_ == "rgb_image" && !dump_video_path_.empty()) {
      dump_image_to_video(msg);
    }
  }

  // CompressedImage callback (RGB compressed image)
  void cb_compressed(const sensor_msgs::msg::CompressedImage::SharedPtr msg) {
    update_arrivals();

    if (should_print()) {
      RCLCPP_INFO(get_logger(),
                  "🗜️  %s received\n"
                  "  • frame_id:        %s\n"
                  "  • stamp (sec):     %.6f\n"
                  "  • format:          %s\n"
                  "  • data size:       %zu\n"
                  "  • recv FPS (1s):   %.1f",
                  topic_type_.c_str(), msg->header.frame_id.c_str(),
                  rclcpp::Time(msg->header.stamp).seconds(),
                  msg->format.c_str(), msg->data.size(), get_fps());
    }
  }

  // CameraInfo callback (camera intrinsic parameters)
  void cb_camerainfo(const sensor_msgs::msg::CameraInfo::SharedPtr msg) {
    // CameraInfo is typically published once; print it once
    std::ostringstream oss;
    oss << "📷 " << topic_type_ << " received\n"
        << "  • frame_id:        " << msg->header.frame_id << "\n"
        << "  • stamp (sec):     " << rclcpp::Time(msg->header.stamp).seconds()
        << "\n"
        << "  • width x height:  " << msg->width << " x " << msg->height << "\n"
        << "  • distortion_model:" << msg->distortion_model << "\n"
        << "  • D: [";
    for (size_t i = 0; i < msg->d.size(); ++i) {
      oss << msg->d[i];
      if (i + 1 < msg->d.size())
        oss << ", ";
    }
    oss << "]\n  • K: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->k[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • R: [";
    for (int i = 0; i < 9; ++i) {
      oss << msg->r[i];
      if (i + 1 < 9)
        oss << ", ";
    }
    oss << "]\n  • P: [";
    for (int i = 0; i < 12; ++i) {
      oss << msg->p[i];
      if (i + 1 < 12)
        oss << ", ";
    }
    oss << "]\n"
        << "  • binning_x: " << msg->binning_x << "\n"
        << "  • binning_y: " << msg->binning_y << "\n"
        << "  • roi: { x_offset: " << msg->roi.x_offset
        << ", y_offset: " << msg->roi.y_offset
        << ", height: " << msg->roi.height << ", width: " << msg->roi.width
        << ", do_rectify: " << (msg->roi.do_rectify ? "true" : "false") << " }";
    RCLCPP_INFO(get_logger(), "%s", oss.str().c_str());
  }

  // Track arrival timestamps to compute FPS
  void update_arrivals() {
    const rclcpp::Time now = this->get_clock()->now();
    arrivals_.push_back(now);
    while (!arrivals_.empty() && (now - arrivals_.front()).seconds() > 1.0) {
      arrivals_.pop_front();
    }
  }
  double get_fps() const { return static_cast<double>(arrivals_.size()); }

  // Control printing frequency
  bool should_print() {
    const rclcpp::Time now = this->get_clock()->now();
    if ((now - last_print_).seconds() >= 1.0) {
      last_print_ = now;
      return true;
    }
    return false;
  }

  // Dump received images to a video file (RGB images only)
  void dump_image_to_video(const sensor_msgs::msg::Image::SharedPtr &msg) {
    cv::Mat image;
    try {
      // Obtain the Mat without copying by not specifying encoding
      cv_bridge::CvImageConstPtr cvp = cv_bridge::toCvShare(msg);
      image = cvp->image;
      // Convert to BGR for uniform saving
      if (msg->encoding == "rgb8") {
        cv::cvtColor(image, image, cv::COLOR_RGB2BGR);
      } else {
        RCLCPP_WARN(get_logger(), "image encoding not expected: %s",
                    msg->encoding.c_str());
        return;
      }
      if (with_mask_) {
        image.setTo(cv::Scalar(0, 0, 0), mask_image_ == 0);
      }
    } catch (const std::exception &e) {
      RCLCPP_WARN(get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }

    // Initialize VideoWriter
    if (!video_writer_.isOpened()) {
      int fourcc = cv::VideoWriter::fourcc('M', 'J', 'P', 'G');
      double fps = std::max(1.0, get_fps());
      bool ok = video_writer_.open(dump_video_path_, fourcc, fps,
                                   cv::Size(image.cols, image.rows), true);
      if (!ok) {
        RCLCPP_ERROR(get_logger(), "Failed to open video file: %s",
                     dump_video_path_.c_str());
        dump_video_path_.clear(); // stop trying
        return;
      }
      RCLCPP_INFO(get_logger(), "VideoWriter started: %s, size=%dx%d, fps=%.1f",
                  dump_video_path_.c_str(), image.cols, image.rows, fps);
    }
    video_writer_.write(image);
  }

  // Member variables
  std::string topic_type_;
  std::string topic_name_;
  std::string dump_video_path_;
  bool with_mask_;
  cv::Mat mask_image_;

  // Subscriptions
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_image_;
  rclcpp::Subscription<sensor_msgs::msg::CompressedImage>::SharedPtr
      sub_compressed_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr sub_camerainfo_;

  // FPS statistics
  rclcpp::Time last_print_{0, 0, RCL_ROS_TIME};
  std::deque<rclcpp::Time> arrivals_;

  // Video writer
  cv::VideoWriter video_writer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<HeadRearCameraTopicEcho>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

**使用说明：**

  1. 订阅RGB图像数据：

```bash
ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image
```

  2. 订阅压缩图像数据：

```bash
ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image_compressed
```

  3. 订阅相机内参：

```bash
ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=camera_info
```

  4. 录制视频：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image -p dump_video_path:=$PWD/rear_camera.avi
```

  5. 录制视频并对把手遮挡区域mask处理：

```bash
# dump_video_path的值可改为其他路径, 注意提前创建该文件所在目录才能保存
ros2 run examples echo_camera_head_rear --ros-args -p topic_type:=rgb_image -p with_mask:=true -p dump_video_path:=$PWD/rear_camera.avi
```

**应用场景：**

  * 人脸识别和追踪

  * 目标检测和识别

  * 视觉SLAM

  * 图像处理和计算机视觉算法开发

  * 机器人视觉导航
