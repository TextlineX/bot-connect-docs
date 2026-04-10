# 机器人能力实验室测试记录模板

## 1. 基本信息

- 测试日期：
- 测试人：
- 机器人名称 / 编号：
- 机器人 IP：
- 测试地点：
- 仓库分支：
- AimDK 版本：
- ROS 版本：

## 2. 本轮范围

- 是否执行阶段 1：
- 是否执行阶段 2：
- 是否执行副作用测试：
- 本轮重点能力：
- 本轮跳过能力：

## 3. 前置检查结果

### 3.1 网络与 SSH

- `ping 192.168.88.88`：
- `ssh agi@192.168.88.88`：
- 结论：

### 3.2 ROS / AimDK 环境

- `source /opt/ros/humble/setup.bash`：
- `source /agibot/data/home/agi/aimdk/install/setup.bash`：
- `which ros2`：
- `ros2 topic list`：
- `ros2 service list`：
- 结论：

## 4. 执行命令

### 4.1 本地命令

```text
在这里粘贴本轮实际执行的本地命令
```

### 4.2 机器人端命令

```text
在这里粘贴本轮实际执行的机器人端命令
```

## 5. 自动化结果文件

- 一阶段摘要：
- 一阶段快照：
- 二阶段摘要：
- 二阶段快照：

## 6. 接口判定总表

| Kind | Name | 阶段1 | 阶段2 | 最终结论 | 证据文件 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| topic | `/aima/hal/imu/chest/state` | pass/fail/skip | pass/fail/skip | available / visible_but_unusable / doc_only / blocked_by_environment / skipped_by_policy | `cases/...` |  |
| service | `/aimdk_5Fmsgs/srv/GetVolume` | pass/fail/skip | pass/fail/skip | available / visible_but_unusable / doc_only / blocked_by_environment / skipped_by_policy | `cases/...` |  |

## 7. 人工观察记录

| 能力 | 是否观察到真实效果 | 现场现象 | 结论 |
| --- | --- | --- | --- |
| TTS | 是/否/未测 |  |  |
| 表情 | 是/否/未测 |  |  |
| 视频 | 是/否/未测 |  |  |
| 灯带 | 是/否/未测 |  |  |
| 预设动作 | 是/否/未测 |  |  |

## 8. 失败项分析

### 8.1 环境问题

- 

### 8.2 接口存在但不可用

- 

### 8.3 文档存在但真机未发现

- 

## 9. 可进入项目开发的能力

- 

## 10. 建议下轮复测项

- 

## 11. 最终结论

### 11.1 已确认可用

- 

### 11.2 已确认存在但仍需复测

- 

### 11.3 文档存在但当前真机未证实

- 

### 11.4 本轮阻塞因素

- 
