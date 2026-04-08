import os
import time
import rclpy
from rclpy.node import Node
from aimdk_msgs.srv import PlayTts

# 简单的 TTS 服务封装，可被多个模块复用
class TtsClient(Node):
    def __init__(self, service_name='/aimdk_5Fmsgs/srv/PlayTts'):
        super().__init__('tts_client_bridge')
        self.service_name = service_name
        self.cli = self.create_client(PlayTts, self.service_name)

    def call(self, text: str) -> bool:
        if not self.cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error(f'服务不可用: {self.service_name}')
            return False
        req = PlayTts.Request()
        req.tts_req.text = text
        req.tts_req.domain = 'ws_bridge'
        req.tts_req.trace_id = 'ws_bridge'
        req.tts_req.is_interrupted = True
        req.tts_req.priority_weight = 0
        req.tts_req.priority_level.value = 6
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if not future.done():
            self.get_logger().error('TTS 调用超时')
            return False
        resp = future.result()
        if resp and resp.tts_resp.is_success:
            self.get_logger().info('TTS 播报成功')
            return True
        self.get_logger().error('TTS 播报失败')
        return False

g_rclpy_inited = False
_g_node = None

def send_tts(text: str):
    global g_rclpy_inited, _g_node
    if not g_rclpy_inited:
        rclpy.init(args=None)
        service_name = os.getenv('TTS_SERVICE', '/aimdk_5Fmsgs/srv/PlayTts')
        _g_node = TtsClient(service_name)
        g_rclpy_inited = True
    return _g_node.call(text)


def shutdown():
    global g_rclpy_inited, _g_node
    if g_rclpy_inited:
        _g_node.destroy_node()
        rclpy.shutdown()
        g_rclpy_inited = False
        _g_node = None
