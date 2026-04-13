<a id="id1"></a>

# 4 __快速开始

本章节会通过**编译、调用SDK示例程序** 和**机器人组合控制程序开发** ，说明如何在灵犀 X2 上使用 **AimDK** 进行二次开发。

  * [4.1 阅读用户使用指南，熟悉相关术语及安全注意事项](/official/quickstart/prerequisites)
  * [4.2 完成基础系统配置](/official/quickstart/prerequisites#id2)
  * [4.3 网络连接](/official/quickstart/prerequisites#id3)
  * [4.4 环境安装和配置](/official/quickstart/prerequisites#aimdk-build)
  * [4.5 运行一个代码示例](/official/quickstart/run_example)
    * [4.5.1 获取机器人的当前状态](/official/quickstart/run_example#id1)
    * [4.5.2 让机器人挥手](/official/quickstart/run_example#id2)
  * [4.6 代码编写](/official/quickstart/code_sample)
    * [4.6.1 项目概述](/official/quickstart/code_sample#id2)
    * [4.6.2 在现有SDK工作空间中添加示例](/official/quickstart/code_sample#sdk)
    * [4.6.3 编写控制代码](/official/quickstart/code_sample#id4)
    * [4.6.4 构建与运行](/official/quickstart/code_sample#id8)
    * [4.6.5 代码解析](/official/quickstart/code_sample#id11)
    * [4.6.6 扩展与优化](/official/quickstart/code_sample#id13)
    * [4.6.7 遇到问题时排查解决](/official/quickstart/code_sample#id18)
    * [4.6.8 下一步学习](/official/quickstart/code_sample#id19)
    * [4.6.9 小结](/official/quickstart/code_sample#id20)

小心

机上二开数据存放的注意事项:

  * 目前固件升/降级会清理机器人系统内大部分位置的数据, 注意提前备份

  * 存放在`$HOME`(/agibot/data/home/agi)目录内的数据默认跨固件留存

  * 注意例外1: `$HOME/aimdk*`由系统自动管理，期望跨固件留存的数据避免放入

  * 谨慎使用一键恢复出厂设置类功能, 会强制清除用户数据(包括默认留存位置)
