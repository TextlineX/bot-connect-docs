<a id="aimdk-x2"></a>

# AimDK_X2 简介

**AimDK_X2** 是由 **智元机器人（AgiBot）** 开发的任务编程与扩展框架，旨在为**二次开发者** 提供灵犀X2机器人开放接口与配套工具。通过 AimDK，开发者可以方便地与机器人系统进行交互，控制机器人行为，访问传感器数据，并基于此开发个性化的应用程序和智能功能。

**设计目标**

  * **简化机器人开发流程** —— 提供统一的接口与标准化通信机制，降低开发复杂度；

  * **提升开发效率** —— 支持高层 API 与任务级控制逻辑，快速实现从动作到场景的开发；

  * **降低开发门槛** —— 对非底层开发者友好，Python 与 C++ 双语言支持；

  * **支持模块化扩展** —— 便于集成算法、应用与外部系统，满足多样化的机器人应用需求。

**核心优势**

  * **完整接口体系** ：覆盖机器人控制、感知、运动、交互等核心功能模块；

  * **基于 ROS 2 框架** ：继承其高可靠性与分布式架构优势，支持实时通信与跨平台扩展；

  * **高扩展性与可定制性** ：为教学研究、商业应用及创新场景提供灵活的接口层；

  * **快速上手与开发** ：提供丰富的示例程序与文档，帮助开发者迅速构建并验证功能原型。

  * [1 __关于 AgiBot X2](/official/about/)
    * [1.1 产品简介](/official/about/part_name)
    * [1.2 机器人具体参数](/official/about/robot_specifications)
    * [1.3 计算单元](/official/about/onboard_computer)
    * [1.4 用户调试接口（旗舰版）](/official/about/user_debug_interface)
    * [1.5 二次开发接口（旗舰版）](/official/about/SDK_interface)
    * [1.6 灵犀X2 传感器说明](/official/about/sensor_fov)
    * [1.7 关节活动范围说明](/official/about/joint_name_and_limit)
    * [1.8 坐标系](/official/about/coordinate_system)
  * [2 __操作指南](/official/guide/)
    * [2.1 开机指南](/official/guide/start_up_guide)
    * [2.2 机器人手机APP连接（Agibot Go APP）](/official/guide/robot_connection)
    * [2.3 遥控手柄连接](/official/guide/remote_controller)
    * [2.4 关机指南](/official/guide/shutdown)
  * [3 __获取SDK](/official/get_sdk/)
  * [4 __快速开始](/official/quickstart/)
    * [4.1 阅读用户使用指南，熟悉相关术语及安全注意事项](/official/quickstart/prerequisites)
    * [4.2 完成基础系统配置](/official/quickstart/prerequisites#id2)
    * [4.3 网络连接](/official/quickstart/prerequisites#id3)
    * [4.4 环境安装和配置](/official/quickstart/prerequisites#aimdk-build)
    * [4.5 运行一个代码示例](/official/quickstart/run_example)
    * [4.6 代码编写](/official/quickstart/code_sample)
  * [5 __接口说明](/official/interface/)
    * [5.1 控制模块](/official/interface/control_mod/)
    * [5.2 交互模块](/official/interface/interactor/)
    * [5.3 故障与系统管理模块 (待发布)](/official/interface/FASM/)
    * [5.4 硬件抽象模块](/official/interface/hal/)
    * [5.5 感知模块（待开放）](/official/interface/perception/)
  * [6 __示例代码](/official/examples/)
    * [6.1 Python接口使用示例](/official/examples/python/)
      * [6.1.1 获取机器人模式](/official/examples/python/robot-mode-get)
      * [6.1.2 设置机器人模式](/official/examples/python/robot-mode-set)
      * [6.1.3 设置机器人动作](/official/examples/python/robot-action-set)
      * [6.1.4 夹爪控制](/official/examples/python/gripper)
      * [6.1.5 灵巧手控制](/official/examples/python/hand)
      * [6.1.6 注册二开输入源](/official/examples/python/input-register)
      * [6.1.7 获取当前输入源](/official/examples/python/input-get)
      * [6.1.8 控制机器人走跑](/official/examples/python/locomotion)
      * [6.1.9 关节电机控制](/official/examples/python/joint)
      * [6.1.10 键盘控制机器人](/official/examples/python/motion-keyboard)
      * [6.1.11 拍照](/official/examples/python/camera-photo)
      * [6.1.12 相机推流示例集](/official/examples/python/camera-stream)
      * [6.1.13 头部触摸传感器数据订阅](/official/examples/python/touch-sensor)
      * [6.1.14 激光雷达数据订阅](/official/examples/python/lidar)
      * [6.1.15 播放视频](/official/examples/python/video-playback)
      * [6.1.16 媒体文件播放](/official/examples/python/media-playback)
      * [6.1.17 TTS (文字转语音)](/official/examples/python/tts)
      * [6.1.18 麦克风数据接收](/official/examples/python/microphone)
      * [6.1.19 表情控制](/official/examples/python/emoji)
      * [6.1.20 LED灯带控制](/official/examples/python/led)
    * [6.2 C++接口使用示例](/official/examples/cpp/)
      * [6.2.1 获取机器人模式](/official/examples/cpp/robot-mode-get)
      * [6.2.2 设置机器人模式](/official/examples/cpp/robot-mode-set)
      * [6.2.3 设置机器人动作](/official/examples/cpp/robot-action-set)
      * [6.2.4 夹爪控制](/official/examples/cpp/gripper)
      * [6.2.5 灵巧手控制](/official/examples/cpp/hand)
      * [6.2.6 注册二开输入源](/official/examples/cpp/input-register)
      * [6.2.7 获取当前输入源](/official/examples/cpp/input-get)
      * [6.2.8 机器人走跑控制](/official/examples/cpp/locomotion)
      * [6.2.9 关节电机控制](/official/examples/cpp/joint)
      * [6.2.10 键盘控制机器人](/official/examples/cpp/motion-keyboard)
      * [6.2.11 拍照](/official/examples/cpp/camera-photo)
      * [6.2.12 相机推流示例集](/official/examples/cpp/camera-stream)
      * [6.2.13 头部触摸传感器数据订阅](/official/examples/cpp/touch-sensor)
      * [6.2.14 激光雷达数据订阅](/official/examples/cpp/lidar)
      * [6.2.15 播放视频](/official/examples/cpp/video-playback)
      * [6.2.16 媒体文件播放](/official/examples/cpp/media-playback)
      * [6.2.17 TTS (文字转语音)](/official/examples/cpp/tts)
      * [6.2.18 麦克风数据接收](/official/examples/cpp/microphone)
      * [6.2.19 表情控制](/official/examples/cpp/emoji)
      * [6.2.20 LED灯带控制](/official/examples/cpp/led)
  * [7 __FAQ](/official/faq/)
  * [8 __特殊过渡方案声明](/official/faq/temp_works)
    * [8.1 关闭 X2 自带的交互能力，开发您自己的语音系统](/official/faq/temp_works#agent-only-voice)
    * [8.2 机器人运动状态精简，v0.7.x及之前的部分McAction状态码不再支持](/official/faq/temp_works#v0-7-xmcaction)
  * [9 __二次开发边界与声明](/official/end_notes)
