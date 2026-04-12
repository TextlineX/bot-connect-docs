<a id="id1"></a>

# 4.6 代码编写

**本节将带您开发一个简单的机器人控制程序，实现机器人X2的手部动作序列和语音播报功能。**

<a id="id2"></a>

## 4.6.1 项目概述

在本项目中，我们将开发一个Python程序，通过ROS 2接口控制机器人X2执行以下动作序列：

  1. 执行第一个动作（挥手）

  2. 语音播报

  3. 执行第二个动作（握手）

**前提条件** ： 与上一节相同, 需要机器人处于稳定站立状态

这个项目将帮助您理解如何通过SDK控制机器人的手部动作序列和交互功能，为后续开发更复杂的任务打下基础。

<a id="sdk"></a>

## 4.6.2 在现有SDK工作空间中添加示例

我们将在现有的SDK工作空间中添加一个新的示例程序，这样可以：

  * 复用现有的构建系统

  * 保持代码组织的一致性

  * 简化构建和运行流程

<a id="id3"></a>

### 了解现有结构

SDK工作空间结构如下：

```bash
aimdk/
├── src/
│   ├── examples/          # C++示例
│   │   ├── src/
│   │   │   ├── hal/       # 硬件抽象层示例
│   │   │   ├── mc/        # 运动控制示例
│   │   │   └── interaction/ # 交互功能示例
│   │   └── CMakeLists.txt
│   └── py_examples/       # Python示例
│       ├── py_examples/
│       └── setup.py
```

小心

机上二开数据存放的注意事项:

  * 目前固件升/降级会清理机器人系统内大部分位置的数据, 注意提前备份

  * 存放在`$HOME`(/agibot/data/home/agi)目录内的数据默认跨固件留存

  * 注意例外1: `$HOME/aimdk*`由系统自动管理，期望跨固件留存的数据避免放入

  * 谨慎使用一键恢复出厂设置类功能, 会强制清除用户数据(包括默认留存位置)

<a id="python"></a>

### 添加新的Python示例

我们将在`py_examples`目录下添加一个新的示例程序：

```bash
# 进入SDK目录
# 注意将以下路径替换为解压后实际路径
cd /path/to/aimdk

# 在py_examples目录下创建新的示例文件
touch src/py_examples/py_examples/action_sequence_demo.py
```

<a id="id4"></a>

## 4.6.3 编写控制代码

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

<a id="id5"></a>

### 创建机器人控制类

在`src/py_examples/py_examples/action_sequence_demo.py`文件中编写以下代码：

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import time

from aimdk_msgs.srv import SetMcPresetMotion, PlayTts
from aimdk_msgs.msg import (
    RequestHeader, McPresetMotion, McControlArea, CommonState,
    TtsPriorityLevel
)

class ActionSequenceDemo(Node):
    def __init__(self):
        super().__init__('action_sequence_demo')
        
        # 创建服务客户端
        self.set_preset_motion_client = self.create_client(
            SetMcPresetMotion, '/aimdk_5Fmsgs/srv/SetMcPresetMotion')
        self.play_tts_client = self.create_client(
            PlayTts, '/aimdk_5Fmsgs/srv/PlayTts')
        
        self.get_logger().info('Action Sequence Demo 已创建')
        
        # 等待服务可用
        while not self.set_preset_motion_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待预设动作服务...')
        while not self.play_tts_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待TTS服务...')
    
    
    def perform_preset_motion(self, area_id, motion_id):
        """执行预设动作"""
        request = SetMcPresetMotion.Request()
        request.header = RequestHeader()
        request.header.stamp = self.get_clock().now().to_msg()
        
        motion = McPresetMotion()
        motion.value = motion_id
        area = McControlArea()
        area.value = area_id
        
        request.motion = motion
        request.area = area
        request.interrupt = False
        
        self.get_logger().info(f'执行预设动作: 区域={area_id}, 动作={motion_id}')
        future = self.set_preset_motion_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            response = future.result()
            if response.response.header.code == 0:
                self.get_logger().info('预设动作执行成功')
                return True
            else:
                self.get_logger().error('预设动作执行失败')
                return False
        else:
            self.get_logger().error('预设动作服务调用失败')
            return False
    
    
    def speak(self, text):
        """控制机器人语音播报"""
        if not self.play_tts_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('TTS服务不可用')
            return False
        
        request = PlayTts.Request()
        request.header.header.stamp = self.get_clock().now().to_msg()
        
        # 设置TTS请求参数
        request.tts_req.text = text
        request.tts_req.domain = 'action_sequence_demo'  # 调用方标识
        request.tts_req.trace_id = 'sequence'            # 请求ID
        request.tts_req.is_interrupted = True            # 是否打断同等优先级播报
        request.tts_req.priority_weight = 0
        request.tts_req.priority_level = TtsPriorityLevel()
        request.tts_req.priority_level.value = 6         # 优先级级别
        
        self.get_logger().info(f'语音播报: {text}')
        future = self.play_tts_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        
        if future.result() is not None:
            response = future.result()
            if response.tts_resp.is_success:
                self.get_logger().info('语音播报成功')
                return True
            else:
                self.get_logger().error('语音播报失败')
                return False
        else:
            self.get_logger().error('TTS服务调用失败')
            return False
    
    def wave_hand(self):
        """控制机器人挥手"""
        # 使用预设动作：右手挥手 (区域=2, 动作=1002)
        return self.perform_preset_motion(2, 1002)
    
    def shake_hand(self):
        """控制机器人握手"""
        # 使用预设动作：右手握手 (区域=2, 动作=1003)
        return self.perform_preset_motion(2, 1003)
    
    def perform_action_sequence(self):
        """执行完整的动作序列流程"""
        self.get_logger().info('开始执行动作序列流程...')
        self.get_logger().info('前提条件：机器人已处于站立状态')
        
        # 1. 第一个动作：挥手
        if not self.wave_hand():
            self.get_logger().error('挥手失败')
            return False
        time.sleep(5)  # 等待挥手完成
        
        # 2. 语音播报
        if not self.speak('你好！我是灵犀X2，现在开始演示手部动作序列！'):
            self.get_logger().error('语音播报失败')
            return False
        time.sleep(3)  # 等待语音播报
        
        # 3. 第二个动作：握手
        if not self.shake_hand():
            self.get_logger().error('握手失败')
            return False
        time.sleep(3)  # 等待握手完成
        
        self.get_logger().info('动作序列流程执行完成')
        return True
```

<a id="id6"></a>

### 添加主程序入口

在同一个文件中添加主程序入口：

```python
def main(args=None):
    rclpy.init(args=args)
    demo = ActionSequenceDemo()
    
    # 执行动作序列流程
    demo.perform_action_sequence()
    
    # 关闭ROS节点
    demo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

<a id="id7"></a>

### 注册到构建系统

为了让新示例能够通过`ros2 run`命令运行，需要在`setup.py`中添加入口点：

```python
# 在 src/py_examples/setup.py 的 entry_points 中添加：
"action_sequence_demo = py_examples.action_sequence_demo:main",
```

完整的entry_points部分应该包含：

```python
entry_points={
    "console_scripts": [
        # ... 现有条目 ...
        "action_sequence_demo = py_examples.action_sequence_demo:main",
    ],
},
```

<a id="id8"></a>

## 4.6.4 构建与运行

<a id="id9"></a>

### 构建项目

```bash
# 进入SDK目录
# 注意将以下路径替换为解压后实际路径
cd /path/to/aimdk

# 设置环境变量
source /opt/ros/humble/setup.bash

# 构建项目
colcon build --packages-select py_examples
```

<a id="id10"></a>

### 运行项目

```bash
# 设置环境变量
source install/local_setup.bash

# 运行新的示例程序
ros2 run py_examples action_sequence_demo
```

<a id="id11"></a>

## 4.6.5 代码解析

<a id="id12"></a>

### 机器人控制类

`ActionSequenceDemo`类是机器人控制的核心，提供了以下功能：

  * **初始化ROS节点和服务客户端** ：在构造函数中，创建ROS节点和必要的服务客户端。

  * **执行预设动作** ：通过`perform_preset_motion`方法，我们可以执行预定义的动作。

  * **语音播报** ：通过`speak`方法

  * **控制机器人动作** ：提供了`wave_hand`和`shake_hand`等方法，用于控制机器人的手部动作。

  * **动作序列执行** ：通过`perform_action_sequence`方法，按顺序执行挥手→说话→握手流程。

<a id="id13"></a>

## 4.6.6 扩展与优化

<a id="id14"></a>

### 添加更多动作和交互

您可以参考现有的代码，添加更多的机器人动作和交互功能，例如：

  * 飞吻 (预设动作ID: 1004)

  * 敬礼 (预设动作ID: 1013)

  * 比心 (预设动作ID: 1007)

  * 举手 (预设动作ID: 1001)

  * 更多语音内容

  * 表情控制

  * 等等

<a id="id15"></a>

### 添加参数配置

您可以通过ROS 2的参数系统，使动作的参数可配置：

```python
# 在构造函数中添加参数声明
self.declare_parameter('wave_count', 3)
self.declare_parameter('wait_duration', 3.0)

# 在方法中使用参数
wait_duration = self.get_parameter('wait_duration').value
time.sleep(wait_duration)
```

<a id="id16"></a>

### 添加错误处理

您可以参考例程序[获取机器人模式](/official/examples/python/robot-mode-get)添加更多的错误处理逻辑，使程序更加健壮：

```python
    def send_request(self):
        request = GetMcAction.Request()
        request.request = CommonRequest()

        self.get_logger().info('📨 Sending request to get robot mode')
        for i in range(8):
            request.request.header.stamp = self.get_clock().now().to_msg()
            future = self.client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=0.25)

            if future.done():
                break

            # retry as remote peer is NOT handled well by ROS
            self.get_logger().info(f'trying ... [{i}]')

        response = future.result()
        if response is None:
            self.get_logger().error('❌ Service call failed or timed out.')
            return

        self.get_logger().info('✅ Robot mode get successfully.')
        self.get_logger().info(f'Mode name: {response.info.action_desc}')
        self.get_logger().info(f'Mode status: {response.info.status.value}')
```

<a id="id17"></a>

### 添加更多交互功能

您可以集成更多交互功能：

```python
# 添加表情服务客户端
from aimdk_msgs.srv import PlayEmoji

# 在动作序列中添加表情
def show_expression(self, emoji_id):
    # 实现表情控制功能
    pass

# 添加更多语音内容
def speak_multiple_messages(self, messages):
    for message in messages:
        self.speak(message)
        time.sleep(1)
```

<a id="id18"></a>

## 4.6.7 遇到问题时排查解决

可以先速查[ FAQ](/official/faq/#faq)部分, 未解决则考虑联系AgiBot X2技术支持。

<a id="id19"></a>

## 4.6.8 下一步学习

完成本节内容后，您可以：

  1. **学习更多示例** ：查看`src/py_examples/py_examples/` 或者 `src/examples/src/`目录下的其他示例程序

  2. **集成感知功能** ：学习如何获取和处理传感器数据

  3. **开发复杂任务** ：结合多个功能模块开发更复杂的机器人应用

<a id="id20"></a>

## 4.6.9 小结

至此，您已经了解到了：

  * ✅ 在现有SDK工作空间中添加新的示例程序

  * ✅ 执行预设动作序列

  * ✅ 实现TTS语音播报功能

  * ✅ 构建和运行自定义示例程序

  * ✅ 控制机器人的手部动作序列：挥手→说话→握手

恭喜您已经掌握了智元机器人X2 AimDK的基本开发技能，包括运动控制、语音交互和动作序列编排，可以开始开发自己的机器人应用了！
