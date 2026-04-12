<a id="faq"></a>

# 7 __FAQ

**Q: 运行例程报错"Package ‘examples’ not found"**

  * 参考[环境安装和配置](/official/quickstart/prerequisites#aimdk-build)和[运行一个代码示例](/official/quickstart/run_example#aimdk-run), 确认aimdk已经顺利编译且source配置

**Q: example构建失败**

  * 找不到colcon则应确保ROS已正确安装, 并正确source配置

  * 检查报错信息, 找不到库则检查依赖安装

  * 清除构建缓存重试

**Q: 通过网线连接机器人后，运行example没有响应？**

  * 尝试`ros2 topic list`以及`ros2 topic echo topic_name`(注意替换`topic_name`为实际topic路径)检查当前状态

  * 预设动作需要确认机器人是否处于稳定站立模式

  * TTS/音频播放问题则检查:

    *       1. 音量是否被关闭, TTS内容、音频格式是否符合接口要求

    *       2. **检查X2 内置的语音交互系统是否被关闭**

**Q: 我直接控制电机时没有响应**

如果执行的是针对HAL层的控制，则需要将MC模块停止工作。

  * `aima em stop-app mc`来停止mc模块。

  * 重新启动代码。

**Q：机器人切换站姿预备（位控站立）模式，下肢没响应，手臂行动缓慢**

  * 电池电量不足导致下肢不上电，更换电量足够的电池。

**Q：调用机器人服务没有响应**

  * 检查对应的服务接口字段是否都正确设置。

**Q: 机器人上使用` cv_bridge`出错(`Assertion failed): s >= 0 in function 'setSize'`)**

  * 请检查编译链接的`OpenCV`版本情况:   
目前机器人环境内同时提供Nvidia源的`OpenCV`和Ubuntu源里的`OpenCV`,   
使用`cv_bridge`需在编译链接时指定Ubuntu源`OpenCV`
