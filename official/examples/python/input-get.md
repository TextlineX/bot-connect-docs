# 6.1.7 获取当前输入源

**该示例中用到了GetCurrentInputSource服务** ，用于获取当前已注册的输入源信息，包括输入源名称、优先级和超时时间等信息。

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from aimdk_msgs.srv import GetCurrentInputSource
from aimdk_msgs.msg import CommonRequest

class GetCurrentInputSourceClient(Node):
    def __init__(self):
        super().__init__('get_current_input_source_client')
        self.client = self.create_client(
            GetCurrentInputSource,
            '/aimdk_5Fmsgs/srv/GetCurrentInputSource'
        )

        self.get_logger().info('✅ GetCurrentInputSource client node created.')

        # Wait for the service to become available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('⏳ Service unavailable, waiting...')

        self.get_logger().info('🟢 Service available, ready to send request.')

    def send_request(self):
        # Create request
        req = GetCurrentInputSource.Request()
        req.request = CommonRequest()

        # Send request and wait for response
        self.get_logger().info('📨 Sending request to get current input source')
        for i in range(8):
            req.request.header.stamp = self.get_clock().now().to_msg()
            future = self.client.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=0.25)

            if future.done():
                break

            # retry as remote peer is NOT handled well by ROS
            self.get_logger().info(f'trying ... [{i}]')

        if not future.done():
            self.get_logger().error('❌ Service call failed or timed out.')
            return False

        response = future.result()
        ret_code = response.response.header.code
        if ret_code == 0:
            self.get_logger().info(
                f'✅ Current input source get successfully:')
            self.get_logger().info(
                f'Name: {response.input_source.name}')
            self.get_logger().info(
                f'Priority: {response.input_source.priority}')
            self.get_logger().info(
                f'Timeout: {response.input_source.timeout}')
            return True
        else:
            self.get_logger().error(
                f'❌ Current input source get failed, return code: {ret_code}')
            return False

def main(args=None):
    rclpy.init(args=args)

    node = None
    try:
        node = GetCurrentInputSourceClient()
        success = node.send_request()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        rclpy.logging.get_logger('main').error(
            f'Program exited with exception: {e}')

    if node:
        node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**使用说明**

```bash
# 获取当前输入源信息
ros2 run py_examples get_current_input_source
```

**输出示例**

```python
[INFO] [get_current_input_source_client]: 当前输入源: node
[INFO] [get_current_input_source_client]: 优先级: 40
[INFO] [get_current_input_source_client]: 超时时间: 1000
```

**注意事项**

  * 确保GetCurrentInputSource服务正常运行

  * 需要在注册输入源之后才能获取到有效信息

  * 状态码为0表示查询成功
