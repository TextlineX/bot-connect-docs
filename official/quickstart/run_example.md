<a id="aimdk-run"></a>

# 4.5 运行一个代码示例

<a id="id1"></a>

## 4.5.1 获取机器人的当前状态

```bash
# 进入 SDK 目录
# 注意将以下路径替换为解压后实际路径
cd /path/to/aimdk

# 设置环境变量
source /opt/ros/humble/setup.bash
source install/local_setup.bash

# 运行示例指令 - 获取机器人当前模式
# 不同示例的运行方式可以具体参考示例说明中的启动说明

# Python 示例
ros2 run py_examples get_mc_action

# C++ 示例
ros2 run examples get_mc_action
```

**输出示例**

如果你看到如下输出，说明你已成功与机器人建立通信，并获取到了机器人的当前运动模式。

```
[INFO] [1764066631.016733611] [get_mc_action_client]: ✅ GetMCAction client node created
[INFO] [1764066631.017900579] [get_mc_action_client]: 🟢 Service available, ready to send request.
[INFO] [1764066631.018566508] [get_mc_action_client]: Sending request to get robot mode
[INFO] [1764066631.021247791] [get_mc_action_client]: Current robot mode:
[INFO] [1764066631.021832667] [get_mc_action_client]: Mode name: PASSIVE_DEFAULT
[INFO] [1764066631.022396136] [get_mc_action_client]: Mode status: 100
```

<a id="id2"></a>

## 4.5.2 让机器人挥手

控制机器人切换至 稳定站立(力控站立)模式, 参考状态流转图完成

<a id="fig-routing-to-stand-default"></a>
    
    
            block-beta
      columns 8
      JD("站姿预备模式\nJOINT DEFAULT"):2 space SD("<span class='highlight-target'>稳定站立模式\nSTAND_DEFAULT</span>"):2 space LD("走跑模式\nLOCOMOTION_DEFAULT"):2
      space:8
      PA("零力矩模式\nPASSIVE_DEFAULT"):2 space:4 LS("越野模式\nLOCOMOTION_STEP"):2
      space:8
      DA("阻尼模式\nDAMPING_DEFAULT"):2 space:6
    
      DA --> PA
      PA --> JD
      JD --> SD
      LD --> SD
      LS --> LD
    
        

重要

在切入稳定站立(`STAND_DEFAULT`)模式前，确保机器人已立起且双脚着地。

```bash
# 1. 切换到站姿预备(位控站立)模式
## python 示例
ros2 run py_examples set_mc_action JD

## 或者 cpp 示例
ros2 run examples set_mc_action JD

# 2. 再切换到稳定站立(力控站立)模式
## python 示例
ros2 run py_examples set_mc_action SD

## 或者 cpp 示例
ros2 run examples set_mc_action SD
```

模式切换到稳定站立后，即可让机器人执行挥手动作:

```bash
## python 示例
ros2 run py_examples preset_motion_client
## cpp 示例
ros2 run examples preset_motion_client
```

**根据提示输入：**

  * **手臂区域 (Arm Area)：** `2` （右臂）

  * **预设动作 ID (Preset Action ID)：** `1002` （挥手）

**预期结果：** 机器人将执行挥手动作！
