# 6.1.2 设置机器人模式

**该示例中用到了SetMcAction服务** ，运行节点程序后终端输入模式对应的字段值，机器人会尝试进入相应的[运动模式](/official/interface/control_mod/modeswitch#tbl-mc-action)。  
**切入稳定站立(` STAND_DEFAULT`)模式前，确保机器人已立起且双脚着地。**   
**模式切换需遵循模式转换图, 跨模式转换不能成功**   
**走跑模式(` LOCOMOTION_DEFAULT`)和稳定站立模式一体化自动切换，按模式转换图流转到两者中较近的即可**

```python
#!/usr/bin/env python3

import sys
import rclpy
import rclpy.logging
from rclpy.node import Node

from aimdk_msgs.srv import SetMcAction
from aimdk_msgs.msg import RequestHeader, CommonState, McAction, McActionCommand

class SetMcActionClient(Node):
    def __init__(self):
        super().__init__('set_mc_action_client')
        self.client = self.create_client(
            SetMcAction, '/aimdk_5Fmsgs/srv/SetMcAction'
        )
        self.get_logger().info('✅ SetMcAction client node created.')

        # Wait for the service to become available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('⏳ Service unavailable, waiting...')

        self.get_logger().info('🟢 Service available, ready to send request.')

    def send_request(self, action_name: str):
        req = SetMcAction.Request()
        req.header = RequestHeader()

        cmd = McActionCommand()
        cmd.action_desc = action_name
        req.command = cmd

        self.get_logger().info(
            f'📨 Sending request to set robot mode: {action_name}')
        for i in range(8):
            req.header.stamp = self.get_clock().now().to_msg()
            future = self.client.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=0.25)

            if future.done():
                break

            # retry as remote peer is NOT handled well by ROS
            self.get_logger().info(f'trying ... [{i}]')

        response = future.result()
        if response is None:
            self.get_logger().error('❌ Service call failed or timed out.')
            return

        if response.response.status.value == CommonState.SUCCESS:
            self.get_logger().info('✅ Robot mode set successfully.')
        else:
            self.get_logger().error(
                f'❌ Failed to set robot mode: {response.response.message}'
            )

def main(args=None):
    action_info = {
        'PASSIVE_DEFAULT': ('PD', 'joints with zero torque'),
        'DAMPING_DEFAULT': ('DD', 'joints in damping mode'),
        'JOINT_DEFAULT': ('JD', 'Position Control Stand (joints locked)'),
        'STAND_DEFAULT': ('SD', 'Stable Stand (auto-balance)'),
        'LOCOMOTION_DEFAULT': ('LD', 'locomotion mode (walk or run)'),
    }

    choices = {}
    for k, v in action_info.items():
        choices[v[0]] = k

    rclpy.init(args=args)
    node = None
    try:
        # Prefer command-line argument, otherwise prompt for input
        if len(sys.argv) > 1:
            motion = sys.argv[1]
        else:
            print('{:<4} - {:<20} : {}'.format('abbr',
                  'robot mode', 'description'))
            for k, v in action_info.items():
                print(f'{v[0]:<4} - {k:<20} : {v[1]}')
            motion = input('Enter abbr of robot mode:')

        action_name = choices.get(motion)
        if not action_name:
            raise ValueError(f'Invalid abbr of robot mode: {motion}')

        node = SetMcActionClient()
        node.send_request(action_name)
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
# 使用命令行参数设置模式（推荐）
ros2 run py_examples set_mc_action JD  # 零力矩模式>>站姿预备（位控站立）
ros2 run py_examples set_mc_action SD  # 机器人已立起且脚着地后方可执行，站姿预备>>稳定站立 
# 稳定站立>>走跑模式 自动切换，无需手动切换

# 或者不带参数运行，程序会提示用户输入双字母缩写代码
ros2 run py_examples set_mc_action
```

**输出示例**

```python
...
[INFO] [1764066567.502968540] [set_mc_action_client]: ✅ Robot mode set successfully.
```

**注意事项**

  * 切入`STAND_DEFAULT`模式前，确保机器人已立起且双脚着地

  * 模式切换可能需要几秒钟时间完成

**接口参考**

  * 服务：`/aimdk_5Fmsgs/srv/SetMcAction`

  * 消息：`aimdk_msgs/srv/SetMcAction`
