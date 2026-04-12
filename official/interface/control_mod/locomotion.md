<a id="id1"></a>

# 5.1.2 走跑控制

**走跑控制接口提供了机器人走跑速度控制的核心功能。**

<a id="id2"></a>

## 控制功能

  * 支持基于横向速度、纵向速度、偏航角速度(YawRate)的走跑控制

  * 支持对多个控制输入源的动态管理、优先级仲裁

<a id="id3"></a>

## 走跑控制话题

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/mc/locomotion/velocity` | `McLocomotionVelocity` | 走跑控制(**稳定站立模式下执行**) | - | -  
  
  * `McLocomotionVelocity` ros2-msg @ mc/motion/McLocomotionVelocity.msg

```
# 走跑控制
# 话题名称: /aima/mc/locomotion/velocity

MessageHeader header             # 消息头
string source                    # 输入源名称，二开自定义, 注意不要和其他模块使用同一名称, 见下方说明
float64 forward_velocity         # 前进/后退速度 (m/s), 前进为正
float64 lateral_velocity         # 左右侧移速度 (m/s), 左为正
float64 angular_velocity         # 偏航角速度 (rad/s), 逆时针为正
```

**注意此处开发者为走跑控制消息的发布者** , 和原生系统内其他模块发出的走跑控制信号(如遥控等)存在竞争冲突的可能。

运控体系提供了针对多输入源的管理机制, 通过优先级实时仲裁控制冲突。

**开发者需注册自定义的输入源并用于走跑控制指令的` source`域**

详见下节[MC控制信号设置](/official/interface/control_mod/MC_control)

走跑控制启动门限制说明:

当机器人静止时, 初始迈步需要开发者下发的目标速度值高于一定门限, 其后保持运动阶段才可以使用更小的目标速度值。目标速度值由`forward_velocity`, `lateral_velocity`, `angular_velocity`计算合成, 使用单一控制量时的门限参考值见下表

<a id="tbl-locomotion-velocity-threshold"></a>

目标速度类型 | 启动门限 | 其他说明  
---|---|---  
`forward_velocity` | 0.09 | 前向后退  
`lateral_velocity` | 0.60 | 绝对值, 左右移均可  
`angular_velocity` | 0.03 | 绝对值, 左右旋均可  

重要

不同固件版本的门限值可能有一定波动, 升级版本时建议确认门限情况, 二开程序预留适配接口

<a id="id4"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ：

    * [机器人走跑控制](/official/examples/cpp/locomotion)

    * [注册二开输入源](/official/examples/cpp/input-register)

  * **Python 示例** ：

    * [控制机器人走跑](/official/examples/python/locomotion)

    * [注册二开输入源](/official/examples/python/input-register)

<a id="id5"></a>

## 安全注意事项

警告

**运动控制限制**

  * 模式切换需要确保机器人处于安全状态

  * 行走控制前需要先注册输入源

  * 建议在仿真环境中先测试运动控制代码

备注

**最佳实践**

  * 实现运动状态监控和异常处理

  * 建议实现运动控制的安全检查

  * 注意速度控制的平滑性和连续性
