# ROS 2 常用指令

在机器人或开发 PC 上通过 SSH 执行，用于调试和排查。

## 环境设置

```bash
# ROS 2 Humble
source /opt/ros/humble/setup.bash

# AIMDK SDK（仅机器人端）
source /agibot/data/home/agi/aimdk/install/local_setup.bash
```

## 节点

```bash
# 查看运行中的节点
ros2 node list

# 查看节点信息
ros2 node info /node_name
```

## 话题（Topic）

```bash
# 列出所有话题
ros2 topic list

# 查看话题消息类型
ros2 topic type /topic_name

# 实时查看话题数据（Ctrl+C 停止）
ros2 topic echo /topic_name

# 查看话题带宽和频率
ros2 topic hz /topic_name
ros2 topic bw /topic_name

# 手动发布话题（测试用）
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}" --once
```

## 服务（Service）

```bash
# 列出所有服务
ros2 service list

# 查看服务类型
ros2 service type /service_name

# 调用服务
ros2 service call /service_name std_srvs/srv/Empty "{}"
```

## 参数

```bash
# 列出节点参数
ros2 param list

# 获取参数值
ros2 param get /node_name parameter_name

# 设置参数值（运行时）
ros2 param set /node_name parameter_name value
```

## 包

```bash
# 列出所有包
ros2 pkg list

# 列出包的节点
ros2 pkg executables | grep package_name
```

## 动作（Action）

```bash
# 查看动作列表
ros2 action list

# 查看动作信息
ros2 action info /action_name

# 发送动作目标
ros2 action send_goal /action_name action_tutorials/action/Fibonacci "{order: 5}"
```

## 启动文件

```bash
# 启动一个 launch 文件
ros2 launch package_name launch_file.py

# 查看可启动的 launch 文件
ros2 pkg executables | grep launch
```

## 运行示例

```bash
# Python 示例（需先 source aimdk）
ros2 run py_examples get_mc_action

# C++ 示例
ros2 run examples set_mc_action JD
```
