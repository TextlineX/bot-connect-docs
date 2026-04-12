# 6.1.13 头部触摸传感器数据订阅

**该示例中用到了 echo_head_touch_sensor** ，通过订阅`/aima/hal/sensor/touch_head`话题来接收机器人的头部触摸传感器的反馈数据。

**功能特点：**

  * 订阅了头部传感器的反馈数据，当头部被触摸时候，输出会从 IDLE->TOUCH

```python
#!/usr/bin/env python3
"""
Head touch state subscription example
"""

import rclpy
from rclpy.node import Node
from aimdk_msgs.msg import TouchState

class TouchStateSubscriber(Node):
    def __init__(self):
        super().__init__('touch_state_subscriber')

        # touch event types
        self.event_type_map = {
            TouchState.UNKNOWN: "UNKNOWN",
            TouchState.IDLE: "IDLE",
            TouchState.TOUCH: "TOUCH",
            TouchState.SLIDE: "SLIDE",
            TouchState.PAT_ONCE: "PAT_ONCE",
            TouchState.PAT_TWICE: "PAT_TWICE",
            TouchState.PAT_TRIPLE: "PAT_TRIPLE"
        }

        # create subscriber
        self.subscription = self.create_subscription(
            TouchState,
            '/aima/hal/sensor/touch_head',
            self.touch_callback,
            10
        )

        self.get_logger().info(
            'TouchState subscriber started, listening to /aima/hal/sensor/touch_head')

    def touch_callback(self, msg):
        event_str = self.event_type_map.get(
            msg.event_type, f"INVALID({msg.event_type})")

        self.get_logger().info(f'Timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d}, '
                               f'Event: {event_str} ({msg.event_type})')

def main(args=None):
    rclpy.init(args=args)
    node = TouchStateSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**使用说明：**

```bash
ros2 run py_examples echo_head_touch_sensor
```

**输出示例：**

```python
[INFO] [1769420383.315173538] [touch_state_subscriber]: Timestamp: 1769420394.129927670, Event: IDLE (1)
[INFO] [1769420383.324978563] [touch_state_subscriber]: Timestamp: 1769420394.139941215, Event: IDLE (1)
[INFO] [1769420383.335265681] [touch_state_subscriber]: Timestamp: 1769420394.149990634, Event: TOUCH (2)
[INFO] [1769420383.344826732] [touch_state_subscriber]: Timestamp: 1769420394.159926892, Event: TOUCH (2)
```
