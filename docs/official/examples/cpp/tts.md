# 6.2.17 TTS (文字转语音)

**该示例中用到了play_tts** ，通过该节点可实现语音播放输入的文字，用户可根据不同的场景输入相应的文本。

**功能特点：**

  * 支持命令行参数和交互式输入

  * 完整的服务可用性检查和错误处理

  * 支持优先级控制和打断机制

  * 提供详细的播放状态反馈

**核心代码**

```cpp
#include <aimdk_msgs/msg/tts_priority_level.hpp>
#include <aimdk_msgs/srv/play_tts.hpp>
#include <iostream>
#include <rclcpp/rclcpp.hpp>
#include <string>

using PlayTTS = aimdk_msgs::srv::PlayTts;

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("play_tts_client_min");

  const std::string service_name = "/aimdk_5Fmsgs/srv/PlayTts";
  auto client = node->create_client<PlayTTS>(service_name);

  // Get text to speak
  std::string tts_text;
  if (argc > 1) {
    tts_text = argv[1];
  } else {
    std::cout << "Enter text to speak: ";
    std::getline(std::cin, tts_text);
    if (tts_text.empty()) {
      tts_text = "Hello, I am AgiBot X2.";
    }
  }

  auto req = std::make_shared<PlayTTS::Request>();
  req->header.header.stamp = node->now();
  req->tts_req.text = tts_text;
  req->tts_req.domain = "demo_client"; // Required: identifies the caller
  req->tts_req.trace_id =
      "demo"; // Optional: request identifier for the TTS request
  req->tts_req.is_interrupted =
      true; // Required: whether to interrupt same-priority playback
  req->tts_req.priority_weight = 0;
  req->tts_req.priority_level.value = 6;

  if (!client->wait_for_service(
          std::chrono::duration_cast<std::chrono::seconds>(
              std::chrono::seconds(5)))) {
    RCLCPP_ERROR(node->get_logger(), "Service unavailable: %s",
                 service_name.c_str());
    rclcpp::shutdown();
    return 1;
  }

  auto future = client->async_send_request(req);
  if (rclcpp::spin_until_future_complete(
          node, future,
          std::chrono::duration_cast<std::chrono::seconds>(
              std::chrono::seconds(10))) != rclcpp::FutureReturnCode::SUCCESS) {
    RCLCPP_ERROR(node->get_logger(), "Call timed out");
    rclcpp::shutdown();
    return 1;
  }

  const auto resp = future.get();
  if (resp->tts_resp.is_success) {
    RCLCPP_INFO(node->get_logger(), "✅ TTS play request succeeded");
  } else {
    RCLCPP_ERROR(node->get_logger(), "❌ TTS play request failed");
  }

  rclcpp::shutdown();
  return 0;
}
```

**使用说明**

```bash
# 使用命令行参数播报文本（推荐）
ros2 run examples play_tts "你好，我是灵犀X2机器人"

# 或者不带参数运行，程序会提示用户输入
ros2 run examples play_tts
```

**输出示例**

```cpp
[INFO] [play_tts_client_min]: ✅ 播报请求成功
```

**注意事项**

  * 确保TTS服务正常运行

  * 支持中文和英文文本播报

  * 优先级设置影响播放队列顺序

  * 打断功能可中断当前播放的语音

**接口参考**

  * 服务：`/aimdk_5Fmsgs/srv/PlayTts`

  * 消息：`aimdk_msgs/srv/PlayTts`
