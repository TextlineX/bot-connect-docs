# 二次开发指南

## 1. 目录结构规范
工作区主要位于 `/home/agi/aimdk/src/`：
- `aimdk_msgs/`: 核心消息定义 (**禁止修改**)。
- `py_examples/`: 官方 Python 示例 (参考使用)。

## 2. 数据存储红线 ⚠️
机器人固件升级会清空大部分目录。
- **❌ 禁止存储**：`/home/agi/aimdk/` 目录下的任何位置（代码除外）。
- **✅ 唯一安全区**：`/agibot/data/home/agi/` (即 `$HOME` 环境变量)。
  - 所有业务数据（照片、日志、配置文件）必须存放在此处。

## 3. 创建独立项目包(二开推荐执行)
```bash
cd ~/aimdk/src
ros2 pkg create --build-type ament_python <你的包名> --dependencies rclpy aimdk_msgs
```

## 4. 接口层与业务层
- **接口层 (骨架)**：
  - 服务名称 (如 `/set_mc_preset_motion`) 和消息类型 (如 `SetMcPresetMotion_Request`) 是固定协议，**严禁修改**。
- **业务层 (肌肉)**：
  - 您可以自由定制参数值 (动作 ID、语音文本)、业务逻辑 (动作编排顺序) 以及辅助功能 (日志、UI)。

## 5. 编译与运行
```bash
# 编译
cd ~/aimdk
colcon build --packages-select <你的包名>
# 刷新环境
source install/setup.bash
# 运行
ros2 run <你的包名> <节点名>
```
