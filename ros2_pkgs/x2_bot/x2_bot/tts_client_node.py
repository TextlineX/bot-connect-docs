#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from aimdk_msgs.srv import PlayTts


class TtsClient(Node):
    def __init__(self):
        super().__init__('x2_bot_tts_client')
        self.declare_parameter('tts_service', '/aimdk_5Fmsgs/srv/PlayTts')
        self.srv_name = self.get_parameter('tts_service').get_parameter_value().string_value
        self.cli = self.create_client(PlayTts, self.srv_name)
        self.get_logger().info(f"[x2_bot] TTS service: {self.srv_name}")

    def send(self, text: str) -> bool:
        if not self.cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(f"服务不可用: {self.srv_name}")
            return False
        req = PlayTts.Request()
        req.tts_req.text = text
        req.tts_req.domain = 'x2_bot'
        req.tts_req.trace_id = 'manual'
        req.tts_req.is_interrupted = True
        req.tts_req.priority_weight = 0
        req.tts_req.priority_level.value = 6
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if not future.done():
            self.get_logger().error("调用超时")
            return False
        resp = future.result()
        ok = bool(resp and resp.tts_resp.is_success)
        self.get_logger().info("✅ 成功" if ok else "❌ 失败")
        return ok


def main(args=None):
    rclpy.init(args=args)
    node = TtsClient()
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("请输入要播报的内容: ").strip() or "你好，我是灵犀X2。"
    node.send(text)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
