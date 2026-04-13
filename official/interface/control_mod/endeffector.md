<a id="id1"></a>

# 5.1.5 末端执行器控制

末端执行器控制目前支持:

  * 灵巧手: 智元OmniHand 灵动款 2025

  * 夹爪: 智元OmniPicker

<a id="id2"></a>

## 手部控制特点

  * **灵巧手模式** : 支持多指协调控制，适合复杂操作

  * **夹爪模式** : 支持开合控制，适合简单抓取

  * **状态监控** : 实时监控手部状态和故障代码

  * **类型查询** : 支持动态查询当前手部类型

<a id="id3"></a>

## 手部控制话题

话题名称 | 消息类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/joint/hand/command` | `HandCommandArray` | 手部控制命令 | - | Hz  
  
  * `HandCommandArray` ros2-msg @ hal/msg/HandCommandArray.msg

```
# 手部控制命令数组
MessageHeader header             # 消息头
HandType left_hand_type          # 左手类型 (1:灵巧手, 2:夹爪)
HandCommand[] left_hands         # 左手命令
HandType right_hand_type         # 右手类型 (1:灵巧手, 2:夹爪)
HandCommand[] right_hands        # 右手命令
```

`HandCommand[]`长度与顺序说明:

<a id="tbl-hand-order"></a>

手类型 | 数组长度 | 顺序 | 补充信息  
---|---|---|---  
夹爪 OmniPicker | 1 | N/A | N/A  
灵巧手 OmniHand | 10 | `ThumbRoll`, `ThumbAbAd`, `ThumbMCP`, `IndexAbAd`, `IndexPIP`, `MiddlePIP`, `RingAbAd`, `RingPIP`, `PinkyAbAd`, `PinkyPIP` | 目前暂时只支持全部关节同时配置，按主动轴索引顺序排列  
    * `HandCommand` ros2-msg @ hal/msg/HandCommand.msg

```
# 手部控制命令
string name                      # 关节名称
float64 position                 # 位置 
float64 velocity                 # 速度
float64 acceleration             # 加速度
float64 deceleration             # 减速度
float64 effort                   # 力矩
```

**注意！该消息内的字段含义和取值范围依具体手类型有较大差异** :

      * 夹爪 OmniPicker:

字段名称 | 取值范围 | 含义说明  
---|---|---  
position | 0.0-1.0浮点数 | 线性映射夹爪张合行程, 1.0完全张开  
velocity | 0.0-1.0浮点数 | 线性映射夹爪运行速度, 1.0最快速度  
acceleration | 0.0-1.0浮点数 | 线性映射夹爪加速度, 1.0最大加速度  
deceleration | 0.0-1.0浮点数 | 线性映射夹爪减速度, 1.0最大减速度  
effort | 0.0-1.0浮点数 | 线性映射夹爪夹持力矩, 1.0最大力矩  
      * 灵巧手 OmniHand:

字段名称 | 取值范围 | 含义说明  
---|---|---  
position | 相应主动轴活动范围, 单位弧度(rad) | 详见灵巧手开发手册  
velocity | N/A | 未使用  
acceleration | N/A | 未使用  
deceleration | N/A | 未使用  
effort | N/A | 未使用  

注意

开发者尝试自主控制手部前, **应确保机器人状态安全后, 禁止PC1上的原生运控模块` aima em stop-app mc`**

手部应用场景如需原生运控模块保持走跑管理等, 可联系技术支持进行系统侧适配

<a id="id4"></a>

## 手部状态信息话题

话题名称 | 消息类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/joint/hand/state` | `HandStateArray` | 手部状态信息 | `TRANSIENT_LOCAL` | 与控制同频率  
  
  * `HandStateArray` ros2-msg @ hal/msg/HandStateArray.msg

```
# 手部状态数组
MessageHeader header             # 消息头
HandType left_hand_type          # 左手类型 (1:灵巧手, 2:夹爪)
HandState[] left_hands           # 左手状态
HandType right_hand_type         # 右手类型 (1:灵巧手, 2:夹爪)
HandState[] right_hands          # 右手状态
```

`HandState[]`长度与顺序说明:

手类型 | 数组长度 | 顺序 | 补充信息  
---|---|---|---  
夹爪 OmniPicker | 1 | N/A | N/A  
灵巧手 OmniHand 灵动款 2025 | 10 | 按主动轴索引顺序排列, 同前述`HandCommand[]` | N/A  
    * `HandState` ros2-msg @ hal/msg/HandState.msg

```
# 手部状态信息
string name                      # 关节名称
float64 position                 # 当前位置
float64 velocity                 # 当前速度
float64 effort                   # 当前力矩
int32 state                      # 状态
int32 faultcode                  # 故障代码
```

**注意！该消息内的字段含义和取值范围依具体手类型有较大差异** :

      * 夹爪 OmniPicker:

字段名称 | 取值范围 | 含义说明  
---|---|---  
position | 0.0-1.0浮点数 | 当前行程，取值范围同前  
velocity | 0.0-1.0浮点数 | 当前速度，取值范围同前  
effort | 0.0-1.0浮点数 | 当前力矩，取值范围同前  
state | 0-已到达目标位置/1-夹爪移动中/2-夹爪堵转/3-物体掉落 | 状态  
faultcode | 0-无故障/1-过温警报/2-超速警报/3-初始化故障警报/4-超限检测警报 | 故障代码  
      * 灵巧手 OmniHand:

字段名称 | 取值范围 | 含义说明  
---|---|---  
position | 弧度(rad) | 当前位置  
velocity | N/A | 暂未使用  
effort | N/A | 当前电流(A), 待实现  
state | N/A | 暂未使用  
faultcode | N/A | 故障代码, 待适配  

<a id="id5"></a>

## 查询手部类型服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/GetHandType` | `GetHandType` | 主动查询手部类型  
  
  * `GetHandType` ros2-srv @ hal/srv/GetHandType.srv

```
# 获取手部类型
# 服务名称: /aimdk_5Fmsgs/srv/GetHandType

# 请求
CommonRequest request            # 通用请求

# 响应
CommonResponse reponse           # 通用响应
HandType left_hands_type         # 左手类型 (1:灵巧手, 2:夹爪)
HandType right_hands_type        # 右手类型 (1:灵巧手, 2:夹爪)
```

`HandType`定义同前, 0x0-无, 0x1-灵巧手, 0x2-夹爪, 0xFF-错误

<a id="id6"></a>

## 编程示例

详细的编程示例和代码说明请参考:

  * **C++ 示例** : [夹爪控制](/official/examples/cpp/gripper)

  * **Python 示例** : [机器人关节控制示例](/official/examples/python/joint#py-joint-control)

<a id="id7"></a>

## 安全注意事项

警告

  * 手部组件自主控制需关闭原生运控, 请注意接管机器人的其他关节, 做好安全防护

  * 请勿自行修改手部组件的配置, 特殊系统适配需求请联系技术支持

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**
