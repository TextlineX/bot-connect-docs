<a id="id1"></a>

# 5.1.4 预设动作控制

**预设动作控制用于触发并控制机器人执行一系列常见的预定义动作，如挥手、握手、举手等。该接口通过简单的调用，能迅速控制机器人执行特定的动作，适用于常见的交互场景和任务。**

<a id="id2"></a>

## 预设动作控制服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/SetMcPresetMotion` | `SetMcPresetMotion` | 执行预设动作(**请先进入稳定站立模式**)  
  
  * `SetMcPresetMotion` ros2-srv @ mc/motion/srv/SetMcPresetMotion.srv

```
# 执行预设动作
# 服务名称: /aimdk_5Fmsgs/srv/SetMcPresetMotion

# 请求
RequestHeader header             # 请求头
McControlArea area               # 控制区域
McPresetMotion motion            # 预设动作
bool interrupt                   # 是否打断前一个动作
string ani_path                  # 自定义动作地址 (待开放)

---

# 响应
CommonTaskResponse response      # 任务响应
```

其中

    * `McControlArea` ros2-msg @ mc/motion/McControlArea.msg

```
# 控制区域定义
int32 value                      # 区域值
```

    * `McPresetMotion` ros2-msg @ mc/motion/McPresetMotion.msg

```
# 预设动作定义
int32 value                      # 动作值
```

注意: v0.8.0开始`area`原有的分区概念已经弱化, 仅和`motion`联合使用映射具体动作，**目前提供如下组合** 供预设动作控制:

<a id="tbl-preset-motion"></a>

动作名称 | `motion` | `area` | 说明  
---|---|---|---  
右手挥手 | 1002 | 2 | 稳定站立模式下执行  
左手挥手 | 1002 | 1 | 同上  
右手握手 | 1003 | 2 | 同上  
左手握手 | 1003 | 1 | 同上  
右手举手 | 1001 | 2 | 同上  
左手举手 | 1001 | 1 | 同上  
右手飞吻 | 1004 | 2 | 同上  
左手飞吻 | 1004 | 1 | 同上  
鼓掌 | 3017 | 11 | 同上  
右手敬礼 | 1013 | 2 | 同上  
左手敬礼 | 1013 | 1 | 同上  
双手比心 | 1007 | 3 | 同上  
右手比心 | 1007 | 2 | 同上  
左手比心 | 1007 | 1 | 同上  
拥抱 | 3008 | 11 | 同上  
加油 | 3011 | 11 | 同上  
双手平举 | 1010 | 3 | 同上  
右手平举 | 1010 | 2 | 同上  
左手平举 | 1010 | 1 | 同上  
拜拜 | 3031 | 11 | 同上  
动感光波 | 3007 | 11 | 同上  
右手击掌 | 1008 | 2 | 同上  
左手击掌 | 1008 | 1 | 同上  
双手打叉 | 3009 | 11 | 同上  
胸前右手挥手 | 1011 | 2 | 同上  
胸前左手挥手 | 1011 | 1 | 同上  
鞠躬 | 3001 | 11 | 同上  
挠头 | 3024 | 11 | 同上  
抓屁股 | 3025 | 11 | 同上  
    * `CommonTaskResponse` ros2-msg @ common/CommonTaskResponse.msg

```
# 内嵌response msg

ResponseHeader header  # 响应头
uint64 task_id  # 任务ID
CommonState state  # 状态
```

      * `ResponseHeader` ros2-msg @ common/ResponseHeader.msg

```
builtin_interfaces/Time stamp
int64 code  # (0:成功,其他-失败)
```

基于`response.header.code`判断请求成功与否

<a id="id3"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ： [设置机器人动作](/official/examples/cpp/robot-action-set)

  * **Python 示例** ： [设置机器人动作](/official/examples/python/robot-action-set)

<a id="id4"></a>

## 安全注意事项

警告

**动作执行限制**

  * 某些动作可能需要特定的机器人姿态，请确保机器人处于安全状态

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

**最佳实践**

  * 使用`interrupt=true`可以打断当前正在执行的动作

  * 建议根据交互场景选择合适的动作和区域
