# 容器环境修复指南

## 问题描述
在 Docker 容器内运行 ROS2 节点时，常遇到检测不到话题、无法导入消息类型或 Python 导入符号未定义等问题。

## 根本原因
容器启动后，系统环境变量（如 `LD_LIBRARY_PATH` 和 `PYTHONPATH`）未指向机器人特有的核心库和消息定义路径。

## 解决方案

### 1. 加载基础环境
```bash
source /opt/ros/humble/setup.bash
```

### 2. 加载系统消息定义
```bash
source /agibot/software/cloud_proxy/share/aimdk_msgs/local_setup.bash
source /agibot/software/cloud_proxy/share/hal_msgs/local_setup.bash
source /agibot/software/cloud_proxy/share/hds_msgs/local_setup.bash
```

### 3. 配置核心库路径
```bash
export LD_LIBRARY_PATH="/agibot/software/cloud_proxy/lib:/agibot/software/drp/lib:/agibot/software/hal_imu/lib:/agibot/software/hal_ethercat/lib:$LD_LIBRARY_PATH"
```

### 4. 配置 Python 路径
```bash
export PYTHONPATH="/agibot/software/cloud_proxy/local/lib/python3.10/dist-packages:$PYTHONPATH"
```

## 永久修复脚本
建议创建一个 `fix_robot_env.sh` 脚本并添加到 `.bashrc`：

```bash
#!/bin/bash
# 核心库路径列表
LIB_DIRS=(
    "/agibot/software/cloud_proxy/lib"
    "/agibot/software/drp/lib"
    "/agibot/software/hal_imu/lib"
    "/agibot/software/hal_ethercat/lib"
    # ... 其他库路径
)
for lib_dir in "${LIB_DIRS[@]}"; do
    if [ -d "$lib_dir" ]; then
        export LD_LIBRARY_PATH="$lib_dir:$LD_LIBRARY_PATH"
    fi
done
# 加载消息定义
source /agibot/software/cloud_proxy/share/aimdk_msgs/local_setup.bash
```

## 注意事项
- **加载顺序**：必须先加载系统环境 (`/agibot/software/`)，再加载用户工作空间 (`~/aimdk/install/`)，否则可能导致版本冲突。
