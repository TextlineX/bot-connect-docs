# 6.2.1 获取机器人模式

通过调用`GetMcAction`服务获取机器人当前的运行模式，包括名称和状态信息。

[运动模式定义](/official/interface/control_mod/modeswitch#tbl-mc-action)

```cpp
#include "aimdk_msgs/srv/get_mc_action.hpp"
#include "aimdk_msgs/msg/common_request.hpp"
#include "aimdk_msgs/msg/response_header.hpp"
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <memory>
#include <signal.h>

// Global variable used for signal handling
std::shared_ptr<rclcpp::Node> g_node = nullptr;

// Signal handler function
void signal_handler(int signal) {
  if (g_node) {
    RCLCPP_INFO(g_node->get_logger(), "Received signal %d, shutting down...",
                signal);
    g_node.reset();
  }
  rclcpp::shutdown();
  exit(signal);
}

class GetMcActionClient : public rclcpp::Node {
public:
  GetMcActionClient() : Node("get_mc_action_client") {

    client_ = this->create_client<aimdk_msgs::srv::GetMcAction>(
        "/aimdk_5Fmsgs/srv/GetMcAction"); // correct the service path
    RCLCPP_INFO(this->get_logger(), "✅ GetMcAction client node created.");

    while (!client_->wait_for_service(std::chrono::seconds(2))) {
      RCLCPP_INFO(this->get_logger(), "⏳ Service unavailable, waiting...");
    }
    RCLCPP_INFO(this->get_logger(),
                "🟢 Service available, ready to send request.");
  }

  void send_request() {
    try {
      auto request = std::make_shared<aimdk_msgs::srv::GetMcAction::Request>();
      request->request = aimdk_msgs::msg::CommonRequest();

      RCLCPP_INFO(this->get_logger(), "📨 Sending request to get robot mode");

      // Set a service call timeout
      const std::chrono::milliseconds timeout(250);
      for (int i = 0; i < 8; i++) {
        request->request.header.stamp = this->now();
        auto future = client_->async_send_request(request);
        auto retcode = rclcpp::spin_until_future_complete(shared_from_this(),
                                                          future, timeout);
        if (retcode != rclcpp::FutureReturnCode::SUCCESS) {
          // retry as remote peer is NOT handled well by ROS
          RCLCPP_INFO(this->get_logger(), "trying ... [%d]", i);
          continue;
        }
        // future.done
        auto response = future.get();
        RCLCPP_INFO(this->get_logger(), "✅ Robot mode get successfully.");
        RCLCPP_INFO(this->get_logger(), "Mode name: %s",
                    response->info.action_desc.c_str());
        RCLCPP_INFO(this->get_logger(), "Mode status: %d",
                    response->info.status.value);
        return;
      }
      RCLCPP_ERROR(this->get_logger(), "❌ Service call failed or timed out.");
    } catch (const std::exception &e) {
      RCLCPP_ERROR(this->get_logger(), "Exception occurred: %s", e.what());
    }
  }

private:
  rclcpp::Client<aimdk_msgs::srv::GetMcAction>::SharedPtr client_;
};

int main(int argc, char *argv[]) {
  try {
    rclcpp::init(argc, argv);

    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Create node
    g_node = std::make_shared<GetMcActionClient>();
    auto client = std::dynamic_pointer_cast<GetMcActionClient>(g_node);
    if (client) {
      client->send_request();
    }

    // Clean up resources
    g_node.reset();
    rclcpp::shutdown();

    return 0;
  } catch (const std::exception &e) {
    RCLCPP_ERROR(rclcpp::get_logger("main"),
                 "Program exited with exception: %s", e.what());
    return 1;
  }
}
```

**使用说明**

```bash
ros2 run examples get_mc_action
```

**输出示例**

```cpp
...
[INFO] [1764066631.021247791] [get_mc_action_client]: Current robot mode:
[INFO] [1764066631.021832667] [get_mc_action_client]: Mode name: PASSIVE_DEFAULT
[INFO] [1764066631.022396136] [get_mc_action_client]: Mode status: 100
```

**接口参考**

  * 服务：`/aimdk_5Fmsgs/srv/GetMcAction`

  * 消息：`aimdk_msgs/srv/GetMcAction`
