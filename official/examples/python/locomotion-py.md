## 6.1.8 控制机器人走跑

**该示例中用到了mc_locomotion_velocity，以下示例通过发布` /aima/mc/locomotion/velocity`话题控制机器人的行走,对于v0.7之后的版本，实现速度控制前需要注册输入源（该示例已实现注册输入源），具体注册步骤可参考代码。**

进入稳定站立模式后执行本程序
    
    
```python
      1#!/usr/bin/env python3
      2
      3import rclpy
      4from rclpy.node import Node
      5import time
      6import signal
      7import sys
      8
      9from aimdk_msgs.msg import McLocomotionVelocity, MessageHeader
     10from aimdk_msgs.srv import SetMcInputSource
     11
     12
     13class DirectVelocityControl(Node):
     14    def __init__(self):
     15        super().__init__('direct_velocity_control')
     16
     17        self.publisher = self.create_publisher(
     18            McLocomotionVelocity, '/aima/mc/locomotion/velocity', 10)
     19        self.client = self.create_client(
     20            SetMcInputSource, '/aimdk_5Fmsgs/srv/SetMcInputSource')
     21
     22        self.forward_velocity = 0.0
     23        self.lateral_velocity = 0.0
     24        self.angular_velocity = 0.0
     25
     26        self.max_forward_speed = 1.0
     27        self.min_forward_speed = 0.2
     28
     29        self.max_lateral_speed = 1.0
     30        self.min_lateral_speed = 0.2
     31
     32        self.max_angular_speed = 1.0
     33        self.min_angular_speed = 0.1
     34
     35        self.timer = None
     36
     37        self.get_logger().info("Direct velocity control node started!")
     38
     39    def start_publish(self):
     40        if not self.timer:
     41            self.timer = self.create_timer(0.02, self.publish_velocity)
     42
     43    def register_input_source(self):
     44        self.get_logger().info("Registering input source...")
     45
     46        timeout_sec = 8.0
     47        start = self.get_clock().now().nanoseconds / 1e9
     48
     49        while not self.client.wait_for_service(timeout_sec=2.0):
     50            now = self.get_clock().now().nanoseconds / 1e9
     51            if now - start > timeout_sec:
     52                self.get_logger().error("Waiting for service timed out")
     53                return False
     54            self.get_logger().info("Waiting for input source service...")
     55
     56        req = SetMcInputSource.Request()
     57        req.action.value = 1001
     58        req.input_source.name = "node"
     59        req.input_source.priority = 40
     60        req.input_source.timeout = 1000
     61
     62        for i in range(8):
     63            req.request.header.stamp = self.get_clock().now().to_msg()
     64            future = self.client.call_async(req)
     65            rclpy.spin_until_future_complete(self, future, timeout_sec=0.25)
     66
     67            if future.done():
     68                break
     69
     70            # retry as remote peer is NOT handled well by ROS
     71            self.get_logger().info(f"trying to register input source... [{i}]")
     72
     73        if future.done():
     74            try:
     75                response = future.result()
     76                state = response.response.state.value
     77                self.get_logger().info(
     78                    f"Input source set successfully: state={state}, task_id={response.response.task_id}")
     79                return True
     80            except Exception as e:
     81                self.get_logger().error(f"Service call exception: {str(e)}")
     82                return False
     83        else:
     84            self.get_logger().error("Service call failed or timed out")
     85            return False
     86
     87    def publish_velocity(self):
     88        msg = McLocomotionVelocity()
     89        msg.header = MessageHeader()
     90        msg.header.stamp = self.get_clock().now().to_msg()
     91        msg.source = "node"
     92        msg.forward_velocity = self.forward_velocity
     93        msg.lateral_velocity = self.lateral_velocity
     94        msg.angular_velocity = self.angular_velocity
     95
     96        self.publisher.publish(msg)
     97
     98        self.get_logger().info(
     99            f"Publishing velocity: forward {self.forward_velocity:.2f} m/s, "
    100            f"lateral {self.lateral_velocity:.2f} m/s, "
    101            f"angular {self.angular_velocity:.2f} rad/s"
    102        )
    103
    104    def set_forward(self, forward):
    105        # check value range, mc has thresholds to start movement
    106        if abs(forward) < 0.005:
    107            self.forward_velocity = 0.0
    108            return True
    109        elif abs(forward) > self.max_forward_speed or abs(forward) < self.min_forward_speed:
    110            raise ValueError("out of range")
    111        else:
    112            self.forward_velocity = forward
    113            return True
    114
    115    def set_lateral(self, lateral):
    116        # check value range, mc has thresholds to start movement
    117        if abs(lateral) < 0.005:
    118            self.lateral_velocity = 0.0
    119            return True
    120        elif abs(lateral) > self.max_lateral_speed or abs(lateral) < self.min_lateral_speed:
    121            raise ValueError("out of range")
    122        else:
    123            self.lateral_velocity = lateral
    124            return True
    125
    126    def set_angular(self, angular):
    127        # check value range, mc has thresholds to start movement
    128        if abs(angular) < 0.005:
    129            self.angular_velocity = 0.0
    130            return True
    131        elif abs(angular) > self.max_angular_speed or abs(angular) < self.min_angular_speed:
    132            raise ValueError("out of range")
    133        else:
    134            self.angular_velocity = angular
    135            return True
    136
    137    def clear_velocity(self):
    138        self.forward_velocity = 0.0
    139        self.lateral_velocity = 0.0
    140        self.angular_velocity = 0.0
    141
    142
    143# Global node instance for signal handling
    144global_node = None
    145
    146
    147def signal_handler(sig, frame):
    148    global global_node
    149    if global_node is not None:
    150        global_node.clear_velocity()
    151        global_node.get_logger().info(
    152            f"Received signal {sig}, clearing velocity and shutting down")
    153    rclpy.shutdown()
    154    sys.exit(0)
    155
    156
    157def main():
    158    global global_node
    159    rclpy.init()
    160
    161    node = DirectVelocityControl()
    162    global_node = node
    163
    164    signal.signal(signal.SIGINT, signal_handler)
    165    signal.signal(signal.SIGTERM, signal_handler)
    166
    167    if not node.register_input_source():
    168        node.get_logger().error("Input source registration failed, exiting")
    169        rclpy.shutdown()
    170        return
    171
    172    # get and check control values
    173    # notice that mc has thresholds to start movement
    174    try:
    175        # get input forward
    176        forward = float(
    177            input("Please enter forward velocity 0 or ±(0.2 ~ 1.0) m/s: "))
    178        node.set_forward(forward)
    179        # get input lateral
    180        lateral = float(
    181            input("Please enter lateral velocity 0 or ±(0.2 ~ 1.0) m/s: "))
    182        node.set_lateral(lateral)
    183        # get input angular
    184        angular = float(
    185            input("Please enter angular velocity 0 or ±(0.1 ~ 1.0) rad/s: "))
    186        node.set_angular(angular)
    187    except Exception as e:
    188        node.get_logger().error(f"Invalid input: {e}")
    189        rclpy.shutdown()
    190        return
    191
    192    node.get_logger().info("Setting velocity, moving for 5 seconds")
    193    node.start_publish()
    194
    195    start = node.get_clock().now()
    196    while (node.get_clock().now() - start).nanoseconds / 1e9 < 5.0:
    197        rclpy.spin_once(node, timeout_sec=0.1)
    198        time.sleep(0.001)
    199
    200    node.clear_velocity()
    201    node.get_logger().info("5-second motion finished, robot stopped")
    202
    203    rclpy.spin(node)
    204    rclpy.shutdown()
    205
    206
    207if __name__ == '__main__':
    208    main()
```
