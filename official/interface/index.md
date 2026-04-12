<a id="id1"></a>

# 5 __接口说明

**智元机器人X2 AimDK接口文档 - 基于ROS2标准的人形机器人开发接口**

智元机器人X2 AimDK 提供了一套完整的ROS2接口，用于控制灵犀X2人形机器人。接口遵循ROS2标准，支持C++和Python两种编程语言，为开发者提供灵活、高效的机器人应用开发环境。

**包结构** aimdk_msgs 协议包按照模块分层，各模块内的 srv、msg 分层不完全一致，但最终都正确链接生成 aimdk_msgs 包对应接口的桩代码。

```bash
aimdk_msgs/interface/robot
├── hal/                    # 硬件抽象层
│   ├── msg/            # 通用消息
│   ├── srv/           # 控制相关服务
│   └── audio/       # 音频相关
├── mc/              # 运控模块
│   ├── action/      # 运动模式相关
│   ├── data/        # 状态量
│   └── motion/       # 运动控制
└── ...                # 更多其他接口
```

**模块概览**

🤖 **控制模块** \- 提供机器人底层控制接口，包括运动控制、关节控制、末端执行器控制等核心功能

  * MC控制信号设置与输入源管理

  * 关节控制与模式切换

  * 预设动作执行

  * 末端执行器控制（夹爪/灵巧手）

🎯 **感知模块（待开放）** \- 提供多模态感知能力，支持视觉、SLAM等感知功能

  * 视觉感知

  * SLAM定位与建图

  * 多传感器融合

💬 **交互模块** \- 提供人机交互接口，支持语音、表情等交互方式

  * 语音识别与合成

  * 表情控制

  * 多媒体播放

🔧 **故障与系统管理（待发布）** \- 提供系统监控、故障诊断和权限管理功能

  * 故障检测与诊断

  * 系统权限管理

  * 系统状态监控

**模块接口**

  * [5.1 控制模块](/official/interface/control_mod/)
    * [5.1.1 运动模式切换](/official/interface/control_mod/modeswitch)
    * [5.1.2 走跑控制](/official/interface/control_mod/locomotion)
    * [5.1.3 MC控制信号设置](/official/interface/control_mod/MC_control)
    * [5.1.4 预设动作控制](/official/interface/control_mod/preset_motion)
    * [5.1.5 末端执行器控制](/official/interface/control_mod/endeffector)
    * [5.1.6 关节控制](/official/interface/control_mod/joint_control)
  * [5.2 交互模块](/official/interface/interactor/)
    * [5.2.1 语音控制](/official/interface/interactor/voice)
    * [5.2.2 屏幕控制](/official/interface/interactor/screen)
    * [5.2.3 灯带控制](/official/interface/interactor/lights)
  * [5.3 故障与系统管理模块 (待发布)](/official/interface/FASM/)
    * [5.3.1 故障处理 （待上线）](/official/interface/FASM/fault)
    * [5.3.2 权限管理 （待上线）](/official/interface/FASM/sudo)
  * [5.4 硬件抽象模块](/official/interface/hal/)
    * [5.4.1 传感器接口](/official/interface/hal/sensor)
    * [5.4.2 电源管理单元 (PMU)](/official/interface/hal/pmu)
  * [5.5 感知模块（待开放）](/official/interface/perception/)
    * [5.5.1 视觉(待发布)](/official/interface/perception/vision)
    * [5.5.2 SLAM (待发布)](/official/interface/perception/SLAM)
