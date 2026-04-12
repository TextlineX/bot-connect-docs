<a id="id1"></a>

# 5.1.1 运动模式切换

**模式切换与走跑控制接口提供了机器人运动模式切换和走跑控制等核心功能。**

<a id="id2"></a>

## 核心功能

支持基础运动模式切换进入:

<a id="tbl-mc-action"></a>

模式 | 取值 | 说明 | 使用场景  
---|---|---|---  
零力矩模式 | `PASSIVE_DEFAULT` | 机器人关节零力矩, 自由状态 | 系统启动、维护, 软急停  
阻尼模式 | `DAMPING_DEFAULT` | 关节有阻尼感 | 安全移动  
位控站立 | `JOINT_DEFAULT` | 位置控制站立 | 精确关节位置控制  
稳定站立 | `STAND_DEFAULT` | 主动发力确保站立 | 动态平衡控制,行走/动作就绪状态  
走跑模式 | `LOCOMOTION_DEFAULT` | 正常走跑 | 日常移动  
  
**注意: v0.8.0+ 稳定站立与走跑模式采用一体化设计, 会根据运动控制情况内部自动切换**

<a id="id3"></a>

## 查询运动模式服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/GetMcAction` | `GetMcAction` | 查询运动模式  
  
  * `GetMcAction` ros2-srv @ mc/action/srv/GetMcAction.srv

```
# 获取运动模式
# 服务名称: /aimdk_5Fmsgs/srv/GetMcAction

# 请求
CommonRequest request            # 通用请求

---

# 响应
ResponseHeader response          # 响应头
McActionInfo info          # 当前运动模式信息
```

    * `McActionInfo` ros2-msg @ mc/action/McActionInfo.msg

```
# 运动模式信息
McAction current_action  # 当前运动模式(v0.8.2开始不再使用)
string action_desc  # 描述
McActionStatus status  # 运动模式的状态
```

      * `McActionStatus` ros2-msg @ mc/action/McActionStatus.msg

```
int32 value  # Action状态 (100:运行中, 200: 切换中)
```

<a id="id4"></a>

## 设置运动模式服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/SetMcAction` | `SetMcAction` | 设置运动模式  
  
  * `SetMcAction` ros2-srv @ mc/motion/srv/SetMcAction.srv

```
# 设置运动模式
# 服务名称: /aimdk_5Fmsgs/srv/SetMcAction

# 请求
RequestHeader header             # 请求头
string source                    # 输入源
McActionCommand command          # 运动命令

---

# 响应
CommonResponse response          # 通用响应, response.status.value为1表成功
```

    * `McActionCommand` ros2-msg @ mc/motion/McActionCommand.msg

```
# McActionCommand
McAction action  # v0.8.2开始不再使用
string action_desc  # 模式描述
```

<a id="id5"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ： [获取机器人模式](/official/examples/cpp/robot-mode-get) [设置机器人模式](/official/examples/cpp/robot-mode-set)

  * **Python 示例** ：[获取机器人模式](/official/examples/python/robot-mode-get) [设置机器人模式](/official/examples/python/robot-mode-set)

<a id="id6"></a>

## 安全注意事项

警告

  * **请勿使用本节未提及的运动模式和模式描述设置**

  * 模式切换需要确保机器人处于安全状态

  * 建议在仿真环境中先测试运动控制代码

  * **运控计算单元(PC1, 10.0.1.40)上切勿部署二开程序** , 以免影响运控等高实时要求的任务

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

**最佳实践**

  * 实现运动状态监控和异常处理

  * 建议实现运动控制的安全检查
