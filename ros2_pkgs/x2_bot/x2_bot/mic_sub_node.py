#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

# 假设音频话题类型为 std_msgs/String 或自定义消息，按需替换
DEFAULT_TOPIC = '/aima/hal/audio/capture'


class MicSub(Node):
    def __init__(self):
        super().__init__('x2_bot_mic_sub')
        self.declare_parameter('audio_topic', DEFAULT_TOPIC)
        topic = self.get_parameter('audio_topic').get_parameter_value().string_value
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
        )
        self.sub = self.create_subscription(String, topic, self.on_msg, qos)
        self.get_logger().info(f"[x2_bot] 监听音频话题: {topic}")

    def on_msg(self, msg: String):
        # 这里只打印长度；可在此写文件或转 ASR
        data_len = len(msg.data) if hasattr(msg, 'data') else 0
        self.get_logger().info(f"[audio] 收到 {data_len} bytes")


def main(args=None):
    rclpy.init(args=args)
    node = MicSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
