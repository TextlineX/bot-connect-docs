import os

import rclpy
from aimdk_msgs.msg import CommonState, McControlArea, McPresetMotion, RequestHeader
from aimdk_msgs.srv import SetMcPresetMotion
from rclpy.node import Node


class PresetMotionClient(Node):
    def __init__(self, service_name="/aimdk_5Fmsgs/srv/SetMcPresetMotion"):
        super().__init__("preset_motion_bridge")
        self.service_name = service_name
        self.cli = self.create_client(SetMcPresetMotion, self.service_name)

    def call(self, motion_id: int, area_id: int, interrupt: bool = False) -> bool:
        if not self.cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error(f"服务不可用: {self.service_name}")
            return False

        req = SetMcPresetMotion.Request()
        req.header = RequestHeader()
        req.motion = McPresetMotion()
        req.motion.value = int(motion_id)
        req.area = McControlArea()
        req.area.value = int(area_id)
        req.interrupt = bool(interrupt)
        req.ani_path = ""

        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if not future.done():
            self.get_logger().error("预设动作调用超时")
            return False

        resp = future.result()
        if not resp:
            self.get_logger().error("预设动作无响应")
            return False

        header = getattr(resp.response, "header", None)
        if header and getattr(header, "code", -1) == 0:
            return True

        state = getattr(resp.response, "state", None)
        if state and getattr(state, "value", None) == CommonState.RUNNING:
            return True

        self.get_logger().error(
            f"预设动作失败 motion_id={motion_id} area_id={area_id} code={getattr(header, 'code', None)}"
        )
        return False


g_rclpy_inited = False
_g_node = None
_owns_rclpy = False


def run_preset(
    name: str,
    motion_id: int | None = None,
    area_id: int | None = None,
    interrupt: bool = False,
):
    del name
    global g_rclpy_inited, _g_node, _owns_rclpy
    if motion_id is None or area_id is None:
        return False
    if not g_rclpy_inited:
        if not rclpy.ok():
            rclpy.init(args=None)
            _owns_rclpy = True
        else:
            _owns_rclpy = False
        service_name = os.getenv("PRESET_MOTION_SERVICE", "/aimdk_5Fmsgs/srv/SetMcPresetMotion")
        _g_node = PresetMotionClient(service_name)
        g_rclpy_inited = True
    return _g_node.call(motion_id, area_id, interrupt=interrupt)


def shutdown():
    global g_rclpy_inited, _g_node, _owns_rclpy
    if g_rclpy_inited:
        _g_node.destroy_node()
        if _owns_rclpy and rclpy.ok():
            rclpy.shutdown()
        g_rclpy_inited = False
        _g_node = None
        _owns_rclpy = False
