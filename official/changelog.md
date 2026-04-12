<a id="id1"></a>

# __版本更新记录

<a id="tbl-changelog"></a>

版本号 | 日期 | 更新提要  
---|---|---  
v0.9.0 (Beta2.0版) | 2026.02.03 | 部分接口用法调整  
示例调优、文档增补  
[明细>>]  
v0.8.2 (Beta1.2版) | 2025.12.10 | **PC1禁止运行二开**  
部分接口用法调整  
示例调优、文档增补  
开放URDF下载  
下线头部关节pitch自由度等  
[明细>>]  
v0.8.1 (Beta1.1版) | 2025.11.11 | 示例调优、文档增补  
开放灯带控制、在线SDK文档阅读  
下线交互相机与播放列表等  
[明细>>]  
v0.8.0 (Beta1.0版) | 2025.11.06 | 部分数据定义与topic变动  
开放关节电机控制、电源监测、头部触摸传感等  
下线体态控制等  
[明细>>]  
v0.7.x (Alpha版) | - | 即将停止维护  
  
* * *

<a id="changelog-v0-9-0"></a>

## Changelog v0.9.0

<a id="id2"></a>

### 新开放功能

  * 固件升降级时, 特定路径支持[用户数据留存](/official/get_sdk/)(**其他位置仍默认清除**)

  * 增加传感器型号信息

<a id="id3"></a>

### 现有功能调整

  * 接口用法调整

    * SetMcAction 增加source域用来标记输入源

    * JointStateArray 增加关节组异常状态域`DomainErrorState state`

    * TtsPriorityLevel 增加新优先级`SYSTEM_L7`用于系统播报

    * `/aimdk_5Fmsgs/srv/PlayVideoGroup`恢复上线

    * `/agent/process_audio_output`(VAD)需要唤醒词激活

  * examples调整

    * 灵巧手示例程序恢复上线

    * 头部触摸传感示例程序上线

    * motocontrol示例关节信息更新

<a id="id4"></a>

### 迭代优化掉的功能

<a id="changelog-v0-8-2"></a>

## Changelog v0.8.2

<a id="id5"></a>

### 新开放功能

  * URDF在线下载

<a id="id6"></a>

### 现有功能调整

  * **运控计算单元(PC1, 10.0.1.40)禁止作为二开程序开发运行环境使用**

  * 接口用法调整

    * SetMcAction/GetMcAction不再使用数字ID代表运控模式, 改用`action_desc`传递运控模式名称

  * examples调整

    * 完善节点shutdown和中断处理

  * 文档说明增补

    * 走跑控制各向启动速度门限调整, 增加变动固件版本后验证新门限的提示

    * 针对ROS Service跨板通信时存在的一些待优化问题, 增加参考例程添加异常处理、快速重试等保护机制的提示

    * 对音视频播放接口使用的文件, 增加关于存放位置的建议和检查访问权限的提示

<a id="id7"></a>

### 迭代优化掉的功能

  * 头部关节暂时下线pitch自由度控制

<a id="changelog-v0-8-1"></a>

## Changelog v0.8.1

<a id="id8"></a>

### 新开放功能

  * 在线SDK文档: <https://x2-aimdk.agibot.com>

  * 交互-灯带控制服务: 胸前LED灯带RGB色彩控制动态/模式控制

    * `/aimdk_5Fmsgs/srv/LedStripCommand`

<a id="id9"></a>

### 现有功能调整

  * example调整

    * 运控相关例程优化通讯流程

    * 相机相关例程加强机器人内系统环境兼容

  * 文档说明增补

    * 接口频率/QoS/带宽等情况的说明

    * 走跑控制各向启动速度门限概念及参考值的说明

    * 手部控制需关闭mc的说明

    * 其他细化调整如路径说明、名词统一化等

<a id="id10"></a>

### 迭代优化掉的功能

  * 交互相机所有接口: 资源占用过高不利于二次开发, 实际功能可被其他相机替代, 涉及topic/service:

    * `/aima/hal/sensor/rgb_head_front_center/camera_info`

    * `/aima/hal/sensor/rgb_head_front_center/rgb_image`

    * `/aima/hal/sensor/rgb_head_front_center/rgb_image/compressed`

  * 头部IMU : 硬件调整, 可用深度相机IMU替代, 涉及topic/service:

    * `/aima/hal/imu/head/state`

  * 播放列表功能, 稳定性修复中暂时下线, 涉及topic/service:

    * `/aimdk_5Fmsgs/srv/PlayEmojiGroup`

    * `/aimdk_5Fmsgs/srv/PlayVideoGroup`

* * *

<a id="changelog-v0-8-0"></a>

## Changelog v0.8.0

<a id="id11"></a>

### 新开放功能

  * 增加底层关节电机控制接口 (支持对’臂/腰/腿’控制及状态查询)

  * 增加供电状态监控接口 (电池BMS,48V/12V输出状态,异常识别-欠压/过流/过温/短路等)

  * 增加头部触摸情况订阅接口

  * 增加系统音量调节接口

  * IMU开放(头/胸/胯)

<a id="id12"></a>

### 现有功能调整

  * 预设动作扩充与编码变动

  * RGBD相机

    * 开放深度图像和rgb图像内参camera info

  * 表情播放升级:

    * ros service调用模式正式上线

    * 提供表情状态订阅(FaceEmojiStatus.msg)

<a id="id13"></a>

### 迭代优化掉的功能

  * 机器人体态控制(McBodyPose.msg)

  * 可用运动模式查询(GetMcAvailableActions.srv)

<a id="id14"></a>

### 其他更新

  * topic变动

    * 深度相机深度图内参 - `/aima/hal/sensor/rgbd_head_front/depth_camera_info`

    * 深度相机rgb图内参 - `/aima/hal/sensor/rgbd_head_front/rgb_camera_info`

    * 表情播放 - `/aimdk_5Fmsgs/srv/PlayEmoji`

    * 视频播放 - `/aimdk_5Fmsgs/srv/PlayVideo`

  * 消息定义变动

    * MC多输入源管理

      1. 修改 SetMcInputSource.srv (添加中间层McInputSource.msg包裹具体参数)

      2. 修改 GetCurrentInputSource.srv (同上)

    * 语音合成

      1. 修改 PlayTts.srv (`tty_xx` -> `tts_xx`)

      2. 修改 TtsResponse (`is_success`域名)

    * 音频播放

      1. 修改 PlayMediaFile.srv (request/response域均更名header, `tty_resp` -> `tts_resp`)

    * 表情播放

      1. 修改 PlayEmoji.srv (`priority`: uint8 -> int32)

    * 视频播放

      1. 修改 PlayVideo.srv (`priority`: uint8 -> int32)
