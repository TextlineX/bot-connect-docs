# 6.2.16 媒体文件播放

**该示例中用到了play_media** ，通过该节点可实现播放指定的媒体文件（如音频文件），支持WAV、MP3等格式的音频文件播放。

**功能特点：**

  * 支持多种音频格式播放（WAV、MP3等）

  * 支持优先级控制，可设置播放优先级

  * 支持打断机制，可中断当前播放

  * 支持自定义文件路径和播放参数

  * 提供完整的错误处理和状态反馈

**技术实现：**

  * 使用PlayMediaFile服务进行媒体文件播放

  * 支持优先级级别设置（0-99）

  * 支持中断控制（is_interrupted参数）

  * 提供详细的播放状态反馈

**应用场景：**

  * 音频文件播放和媒体控制

  * 语音提示和音效播放

  * 多媒体应用开发

  * 机器人交互音频反馈

注意

**⚠️ 请注意！交互计算单元(PC3)独立于二开程序所在的开发计算单元(PC2), 音视频文件务必存入交互计算单元(IP: 10.0.1.42)。**   
**⚠️ 音视频文件夹及该文件夹所有父目录应当为所有用户可访问读取(建议在/var/tmp/下创建子目录存放)**

```cpp
#include <aimdk_msgs/msg/tts_priority_level.hpp>
#include <aimdk_msgs/srv/play_media_file.hpp>
#include <iostream>
#include <rclcpp/rclcpp.hpp>
#include <string>

using PlayMediaFile = aimdk_msgs::srv::PlayMediaFile;

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("play_media_file_client_min");

  // 1) Service name
  const std::string service_name = "/aimdk_5Fmsgs/srv/PlayMediaFile";
  auto client = node->create_client<PlayMediaFile>(service_name);

  // 2) Input file path (prompt user if not provided as argument)
  std::string default_file =
      "/agibot/data/var/interaction/tts_cache/normal/demo.wav";
  std::string file_name;

  if (argc > 1) {
    file_name = argv[1];
  } else {
    std::cout << "Enter the media file path to play (default: " << default_file
              << "): ";
    std::getline(std::cin, file_name);
    if (file_name.empty()) {
      file_name = default_file;
    }
  }

  // 3) Build the request
  auto req = std::make_shared<PlayMediaFile::Request>();
  // CommonRequest request -> RequestHeader header -> builtin_interfaces/Time
  // stamp
  req->header.header.stamp = node->now();

  // PlayMediaFileRequest required fields
  req->media_file_req.file_name = file_name;
  req->media_file_req.domain = "demo_client"; // Required: identifies the caller
  req->media_file_req.trace_id = "demo";      // Optional: request identifier
  req->media_file_req.is_interrupted =
      true; // Whether to interrupt same-priority playback
  req->media_file_req.priority_weight = 0; // Optional: 0~99
  // Priority level: default INTERACTION_L6
  req->media_file_req.priority_level.value = 6;

  // 4) Wait for service and call
  RCLCPP_INFO(node->get_logger(), "Waiting for service: %s",
              service_name.c_str());
  if (!client->wait_for_service(std::chrono::seconds(5))) {
    RCLCPP_ERROR(node->get_logger(), "Service unavailable: %s",
                 service_name.c_str());
    rclcpp::shutdown();
    return 1;
  }

  auto future = client->async_send_request(req);
  auto rc = rclcpp::spin_until_future_complete(node, future,
                                               std::chrono::seconds(10));

  if (rc == rclcpp::FutureReturnCode::INTERRUPTED) {
    RCLCPP_WARN(node->get_logger(), "Interrupted while waiting");
    rclcpp::shutdown();
    return 1;
  }

  if (rc != rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_ERROR(node->get_logger(), "Call timed out or did not complete");
    rclcpp::shutdown();
    return 1;
  }

  // 5) Handle response (success is in tts_resp)
  try {
    const auto resp = future.get();
    bool success = resp->tts_resp.is_success;

    if (success) {
      RCLCPP_INFO(node->get_logger(), "✅ Media file play request succeeded: %s",
                  file_name.c_str());
    } else {
      RCLCPP_ERROR(node->get_logger(), "❌ Media file play request failed: %s",
                   file_name.c_str());
    }
  } catch (const std::exception &e) {
    RCLCPP_ERROR(node->get_logger(), "Call exception: %s", e.what());
  }

  rclcpp::shutdown();
  return 0;
}
```

**使用说明：**

```bash
# 播放默认音频文件
ros2 run examples play_media

# 播放指定音频文件
# 注意替换/path/to/your/audio_file.wav为交互板上实际文件路径
ros2 run examples play_media /path/to/your/audio_file.wav

# 播放TTS缓存文件
ros2 run examples play_media /agibot/data/var/interaction/tts_cache/normal/demo.wav
```

**输出示例：**

```cpp
[INFO] [play_media_file_client_min]: ✅ 媒体文件播放请求成功
```

**注意事项：**

  * 确保音频文件路径正确且文件存在

  * 支持的文件格式：WAV、MP3等

  * 优先级设置影响播放队列顺序

  * 打断功能可中断当前播放的音频
