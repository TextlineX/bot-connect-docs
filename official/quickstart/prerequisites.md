<a id="id1"></a>

# 4.1 阅读用户使用指南，熟悉相关术语及安全注意事项

  * [灵犀 X2 旗舰版用户使用指南](https://www.zhiyuan-robot.com/filepage/291.html)

  * [OmniPicker 使用说明](https://www.zhiyuan-robot.com/DOCS/PM/X1)

  * [OmniHand 灵巧手 2025 用户产品使用说明书](https://www.zhiyuan-robot.com/DOCS/OS/Omnihand-O10)

* * *

<a id="id2"></a>

# 4.2 完成基础系统配置

  * **操作系统** ：Ubuntu 22.04 LTS

  * **ROS2 版本** ：Humble

  * **Python 版本** ：Python 3.8 及以上

  * **C++ 标准** ：C++17

以及SDK例程依赖库:

  * **OpenCV** : 图像处理

  * **Ruckig** : 轨迹规划

  * **ncurses** : 终端控制

  * **libcurl** : 网络通信

  * **cv_bridge** : ROS图像CV图像转换

按SDK使用模式分以下情况:

  * 开发计算单元上直接使用SDK模式, 系统已具备上述条件, 可免安装配置。(快速上手阶段推荐)

  * 上位机运行SDK+跨机组网模式, 则需客户确认上位机符合以上配置。

_上位机安装参考_

  * Ubuntu 22.04 LTS的安装方法请参考[Ubuntu官方安装说明](https://ubuntu.com/tutorials/install-ubuntu-desktop) [官方安装文件下载](https://releases.ubuntu.com/22.04)

  * ROS2 的安装方法请参考[ROS 2官方文档](https://docs.ros.org/en/humble/index.html)

  * Python3/C++ Ubuntu 22.04和ROS Humble默认可满足

* * *

<a id="id3"></a>

# 4.3 网络连接

灵犀 X2 旗舰版支持多种网络接入方式连接机器人内系统：

**（1）通过机器人背部的有线网口直接连接** 使用网线连接[二次开发网口](/official/about/SDK_interface#img-x2-sdk-interface)与上位机端口。

  * 上位机端将网口配置为静态 IP **(10.0.1.2，子网掩码 255.255.255.0)** 。

  * 此时开发计算单元的默认 IP 为 **10.0.1.41** ，可实现 跨机ROS组网 以及 **SSH 登录** （账号密码/密钥请咨询技术支持）。

**（2）通过机器人内置热点 Wi-Fi 连接**

  * 在 **APP** 上开启机器人 **AP 热点** ，并查看 Wi-Fi 名称与密码。

  * 连接该热点后，可通过 **192.168.88.88** 跳板访问开发计算单元（SSH 登录账号密码/密钥请咨询技术支持）。

* * *

注意

**切勿使用运控计算单元(PC1, 10.0.1.40/192.168.88.88)作为二开程序开发运行环境**

注意

上位机运行SDK+跨机组网模式时, 请使用有线直连方式。**无线连接仅可作为SSH终端调试线路使用** 。

重要

不建议将机器人与开发上位机接入含其他设备的公共或复杂网络环境。  
开发者需妥善管理 **网络安全风险** ，以防止设备间通信干扰或数据泄露。

<a id="aimdk-build"></a>

# 4.4 环境安装和配置

将 SDK 放入目标运行环境并解压

```bash
# 设置环境变量 (开发计算单元直接运行模式可跳过本步)
source /opt/ros/humble/setup.bash

# 构建 SDK
# 假设拷贝并解压后到 X2 AimDK 项层目录名称为 aimdk
cd ./aimdk/
colcon build
```

小心

机上二开数据存放的注意事项:

  * 目前固件升/降级会清理机器人系统内大部分位置的数据, 注意提前备份

  * 存放在`$HOME`(/agibot/data/home/agi)目录内的数据默认跨固件留存

  * 注意例外1: `$HOME/aimdk*`由系统自动管理，期望跨固件留存的数据避免放入

  * 谨慎使用一键恢复出厂设置类功能, 会强制清除用户数据(包括默认留存位置)
