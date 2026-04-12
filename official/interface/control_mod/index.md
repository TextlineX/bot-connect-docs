<a id="id1"></a>

# 5.1 控制模块

**智元机器人X2 AimDK 控制模块 - 提供完整的机器人底层控制接口**

控制模块是智元机器人X2 AimDK的核心组件，提供了完整的机器人底层控制接口。该模块遵循ROS2标准，支持C++和Python两种编程语言，为开发者提供灵活、高效的机器人控制能力。

**核心功能**

  * **运动控制** ：多输入源管理、速度控制、模式切换

  * **关节控制** ：关节级控制，支持多种控制模式

  * **末端执行器** ：夹爪和灵巧手控制

  * **预设动作** ：丰富的预设动作库

**接口规范**

  * **服务接口** ：采用`/aimdk_5Fmsgs/srv/`前缀

  * **话题接口** ：大部分采用`/aima/`前缀

  * **消息类型** ：采用`aimdk_msgs`包

  * **编程语言支持** ：C++、Python

  * **消息格式** ：标准ROS2消息格式

**版本兼容性**

  * **当前版本** : v0.8

  * **最低版本** : v0.6 (部分功能)

  * **ROS2版本** : Humble

  * **支持架构** : x86_64, aarch64

**安全注意事项**

警告

**重要安全提醒**

  * 开发速度控制程序时，記得注册输入源

  * 某些关节控制示例需临时关闭MC模块

  * 建议在仿真环境中先测试代码

  * 确保机器人处于安全环境

  * **运控计算单元(PC1, 10.0.1.40)上切勿部署二开程序** , 以免影响运控等高实时要求的任务

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

**功能模块**

  * [5.1.1 运动模式切换](/official/interface/control_mod/modeswitch)
    * [核心功能](/official/interface/control_mod/modeswitch#id2)
    * [查询运动模式服务](/official/interface/control_mod/modeswitch#id3)
    * [设置运动模式服务](/official/interface/control_mod/modeswitch#id4)
    * [编程示例](/official/interface/control_mod/modeswitch#id5)
    * [安全注意事项](/official/interface/control_mod/modeswitch#id6)
  * [5.1.2 走跑控制](/official/interface/control_mod/locomotion)
    * [控制功能](/official/interface/control_mod/locomotion#id2)
    * [走跑控制话题](/official/interface/control_mod/locomotion#id3)
    * [编程示例](/official/interface/control_mod/locomotion#id4)
    * [安全注意事项](/official/interface/control_mod/locomotion#id5)
  * [5.1.3 MC控制信号设置](/official/interface/control_mod/MC_control)
    * [核心特性](/official/interface/control_mod/MC_control#id1)
    * [输入源配置](/official/interface/control_mod/MC_control#id3)
    * [仲裁流程](/official/interface/control_mod/MC_control#id5)
    * [输入源管理服务](/official/interface/control_mod/MC_control#id7)
    * [编程示例](/official/interface/control_mod/MC_control#id8)
    * [注意事项](/official/interface/control_mod/MC_control#id9)
  * [5.1.4 预设动作控制](/official/interface/control_mod/preset_motion)
    * [预设动作控制服务](/official/interface/control_mod/preset_motion#id2)
    * [编程示例](/official/interface/control_mod/preset_motion#id3)
    * [安全注意事项](/official/interface/control_mod/preset_motion#id4)
  * [5.1.5 末端执行器控制](/official/interface/control_mod/endeffector)
    * [手部控制特点](/official/interface/control_mod/endeffector#id2)
    * [手部控制话题](/official/interface/control_mod/endeffector#id3)
    * [手部状态信息话题](/official/interface/control_mod/endeffector#id4)
    * [查询手部类型服务](/official/interface/control_mod/endeffector#id5)
    * [编程示例](/official/interface/control_mod/endeffector#id6)
    * [安全注意事项](/official/interface/control_mod/endeffector#id7)
  * [5.1.6 关节控制](/official/interface/control_mod/joint_control)
    * [核心特性](/official/interface/control_mod/joint_control#id2)
    * [关节控制话题](/official/interface/control_mod/joint_control#id5)
    * [关节状态查询服务](/official/interface/control_mod/joint_control#id6)
    * [编程示例](/official/interface/control_mod/joint_control#id7)
    * [安全注意事项](/official/interface/control_mod/joint_control#id8)
