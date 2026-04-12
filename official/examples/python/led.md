# 6.1.20 LED灯带控制

**功能说明** ：演示如何控制机器人的LED灯带，支持多种显示模式和自定义颜色。

**核心代码** ：

```python
#!/usr/bin/env python3

import sys
import rclpy
import rclpy.logging
from rclpy.node import Node

from aimdk_msgs.msg import CommonRequest
from aimdk_msgs.srv import LedStripCommand

class PlayLightsClient(Node):
    def __init__(self):
        super().__init__('play_lights_client')

        # create service client
        self.client = self.create_client(
            LedStripCommand, '/aimdk_5Fmsgs/srv/LedStripCommand')

        self.get_logger().info('✅ PlayLights client node created.')

        # Wait for the service to become available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('⏳ Service unavailable, waiting...')

        self.get_logger().info('🟢 Service available, ready to send request.')

    def send_request(self, led_mode, r, g, b):
        """Send LED control request"""
        # create request
        request = LedStripCommand.Request()
        request.led_strip_mode = led_mode
        request.r = r
        request.g = g
        request.b = b

        # send request
        # Note: LED strip is slow to response (up to ~5s)
        self.get_logger().info(
            f'📨 Sending request to control led strip: mode={led_mode}, RGB=({r}, {g}, {b})')
        for i in range(4):
            request.request.header.stamp = self.get_clock().now().to_msg()
            future = self.client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5)

            if future.done():
                break

            # retry as remote peer is NOT handled well by ROS
            self.get_logger().info(f'trying ... [{i}]')

        response = future.result()
        if response is None:
            self.get_logger().error('❌ Service call not completed or timed out.')
            return False

        if response.status_code == 0:
            self.get_logger().info('✅ LED strip command sent successfully.')
            return True
        else:
            self.get_logger().error(
                f'❌ LED strip command failed with status: {response.status_code}')
            return False

def main(args=None):
    rclpy.init(args=args)
    node = None

    try:
        # get command line args
        if len(sys.argv) > 4:
            # use CLI args
            led_mode = int(sys.argv[1])
            if led_mode not in (0, 1, 2, 3):
                raise ValueError("invalid mode")
            r = int(sys.argv[2])
            if r < 0 or r > 255:
                raise ValueError("invalid R value")
            g = int(sys.argv[3])
            if g < 0 or g > 255:
                raise ValueError("invalid G value")
            b = int(sys.argv[4])
            if b < 0 or b > 255:
                raise ValueError("invalid B value")
        else:
            # interactive input
            print("=== LED strip control example ===")
            print("Select LED strip mode:")
            print("0 - Steady on")
            print("1 - Breathing (4s cycle, sine brightness)")
            print("2 - Blinking (1s cycle, 0.5s on, 0.5s off)")
            print("3 - Flowing (2s cycle, light up from left to right)")

            led_mode = int(input("Enter mode (0-3): "))
            if led_mode not in (0, 1, 2, 3):
                raise ValueError("invalid mode")

            print("\nSet RGB color values (0-255):")
            r = int(input("Red (R): "))
            if r < 0 or r > 255:
                raise ValueError("invalid R value")
            g = int(input("Green (G): "))
            if g < 0 or g > 255:
                raise ValueError("invalid G value")
            b = int(input("Blue (B): "))
            if b < 0 or b > 255:
                raise ValueError("invalid B value")

        node = PlayLightsClient()
        node.send_request(led_mode, r, g, b)
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

**使用说明** ：

```bash
# 构建
colcon build --packages-select py_examples

# 交互式运行
ros2 run py_examples play_lights

# 命令行参数运行
ros2 run py_examples play_lights 1 255 0 0  # 模式1，红色
```

**输出示例** ：

```python
=== LED灯带控制示例 ===
请选择灯带模式：
0 - 常亮模式
1 - 呼吸模式 (4s周期，亮度正弦变化)
2 - 闪烁模式 (1s周期，0.5s亮，0.5s灭)
3 - 流水模式 (2s周期，从左到右依次点亮)
请输入模式 (0-3): 1

请设置RGB颜色值 (0-255)：
红色分量 (R): 255
绿色分量 (G): 0
蓝色分量 (B): 0

发送LED控制命令...
模式: 1, 颜色: RGB(255, 0, 0)
✅ LED strip command sent successfully
```

**技术特点** ：

  * 支持4种LED显示模式

  * RGB颜色自定义

  * 同步服务调用

  * 命令行参数支持

  * 输入参数验证

  * 友好的用户交互界面
