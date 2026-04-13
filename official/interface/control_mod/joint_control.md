<a id="id1"></a>

# 5.1.6 关节控制

**关节控制接口提供了对机器人各个关节的精确控制能力，支持多种控制模式和关节组。**

<a id="id2"></a>

## 核心特性

<a id="id3"></a>

### 控制模式

  * **位置控制** ：控制关节达到指定角度位置

  * **速度控制** ：控制关节以指定角速度运动

  * **力矩控制** ：控制关节输出指定力矩

<a id="id4"></a>

### 支持关节

  * **左臂关节** ：7个自由度关节（肩部3个、肘部1个、腕部3个）

  * **右臂关节** ：7个自由度关节（肩部3个、肘部1个、腕部3个）

  * **左腿关节** ：6个自由度关节（臀部3个、膝部1个、踝部2个）

  * **右腿关节** ：6个自由度关节（臀部3个、膝部1个、踝部2个）

  * **腰部关节** ：旋转、俯仰、侧弯

  * **头部关节** ：低头抬头暂未发布、左右扭头

<a id="id5"></a>

## 关节控制话题

按部位分组控制关节(手臂、腿、腰、头), 结合状态反馈实现闭环控制

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/joint/*/command` | `JointCommandArray` | 关节控制命令 | - | Hz  
`/aima/hal/joint/*/state` | `JointStateArray` | 关节状态反馈 | `TRANSIENT_LOCAL` | Hz  
  
其中`*`取值为`head`(需硬件支持的头部), `arm`, `waist`, `leg`

  * `JointCommandArray` ros2-msg @ hal/msg/JointCommandArray.msg

```
# 关节控制命令数组
MessageHeader header             # 消息头
JointCommand[] joints            # 关节命令数组
```

    * `JointCommand` ros2-msg @ hal/msg/JointCommand.msg

```
# 关节控制命令
string name                      # 关节名称, 可不填
float64 position                 # 位置 (rad)
float64 velocity                 # 速度 (rad/s)
float64 effort                   # 力矩 (N·m)
float64 stiffness                # 刚度 (N·m/rad)
float64 damping                  # 阻尼 (N·m·s/rad)
```

`JointCommand[]`长度与顺序如下表

<a id="tbl-joint-order"></a>

关节组 | 长度 | 内容 | 补充信息  
---|---|---|---  
head | 2 | `head_yaw`, `head_pitch` | 目前仅yaw有效, pitch占位预留  
waist | 3 | `wrist_yaw`, `wrist_pitch`, `wrist_roll` |   
arm | 7*2 | `shoulder_pitch`, `shoulder_roll`, `shoulder_yaw`, `elbow`, `wrist_yaw`, `wrist_pitch`, `wrist_roll` | 先左半部分所有关节，后右半部分  
leg | 6*2 | `hip_pitch`, `hip_roll`, `hip_yaw`, `knee`, `ankle_pitch`, `ankle_roll` | 先左半部分所有关节，后右半部分  
  * `JointStateArray` ros2-msg @ hal/msg/JointStateArray.msg

```
# 关节状态数组
MessageHeader header             # 消息头
DomainErrorState state           # 关节组异常状态
JointState[] joints              # 关节状态数组
```

    * `DomainErrorState` ros2-msg @ hal/msg/DomainErrorState.msg

```
# 关节组异常状态
uint8 value        # 1: 阻尼模式, 2: 下电模式, 3: 下使能模式, 4: 通信断连, 其他: 无状态
```

<a id="rosmsg-jointstate"></a>

    * `JointState` ros2-msg @ hal/msg/JointState.msg

```
# 关节状态信息
string name                      # 关节名称, 暂未使用
float64 position                 # 位置 (rad)
float64 velocity                 # 速度 (rad/s)
float64 effort                   # 力矩 (N·m)
uint8 coil_temp                  # 线圈温度 (°C)
uint8 motor_temp                 # 电机温度 (°C)
uint8 motor_vol                  # 电机电压 (V)
```

`JointState[]`长度和顺序参见上方`JointCommand[]`关节顺序说明

<a id="id6"></a>

## 关节状态查询服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/GetAllJointState` | `GetAllJointState` | 主动查询关节状态  
  
  * `GetAllJointState` ros2-srv @ hal/srv/GetAllJointState.srv

```
# 获取所有关节状态
# 服务名称: /aimdk_5Fmsgs/srv/GetAllJointState

# 请求
CommonRequest request            # 通用请求

# 响应
CommonResponse reponse           # 通用响应
JointState[] head_joints         # 头部关节状态
JointState[] arm_joints          # 手臂关节状态
JointState[] waist_joints        # 腰部关节状态
JointState[] leg_joints          # 腿部关节状态
```

`JointState[]`长度和顺序参见上方`JointCommand[]`关节顺序说明

<a id="id7"></a>

## 编程示例

详细的编程示例和代码说明请参考:

  * **C++ 示例** : [机器人关节控制示例](/official/examples/cpp/joint#cpp-joint-control)

  * **Python 示例** : [机器人关节控制示例](/official/examples/python/joint#py-joint-control)

<a id="id8"></a>

## 安全注意事项

警告

**关节限制**

  * 所有关节都有运动范围限制，超出范围可能导致机械损坏

  * 建议在控制前检查关节角度是否在安全范围内

  * 使用力矩控制时需特别注意安全限制

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

**最佳实践**

  * 使用平滑的轨迹规划避免突然的关节运动

  * 实现关节状态监控和异常检测

  * 在控制前确保机器人处于安全状态
