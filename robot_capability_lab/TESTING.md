# 机器人能力实验室测试手册

这份手册解决的不是“怎么运行脚本”，而是“怎么把一次测试做成可复现、可交接、可验收的标准流程”。

如果你只是想快速跑命令，看 `README.md` 就够了；如果你要：

- 自己做完整回归
- 交给同事复测
- 给项目做阶段验收
- 把“文档存在”和“真机可用”彻底分开

就按这份手册执行。

## 1. 测试目标

我们要回答 4 个问题：

1. 知识库里写的接口，机器人真机上是否真的存在
2. 接口存在时，是否能稳定读到数据 / 返回结果
3. 当前项目是否已经真正桥接到这个接口
4. 接口是否适合进入后续项目开发

最终每个接口必须落到一个明确结论，不允许只写“好像能用”。

## 2. 测试阶段定义

### 阶段 1：发现性测试

目标：确认接口是否存在、类型是否匹配、有没有基础元数据。

覆盖内容：

- `ros2 topic type`
- `ros2 topic info -v`
- `ros2 interface show`
- `ros2 topic hz`
- 对低风险话题做 `echo --once`
- 对服务做类型和接口定义检查

产物：

- `inventory/generated/runtime_snapshot.json`
- `inventory/generated/runtime_summary.md`
- 各 case 目录下 `runtime.json`

### 阶段 2：低风险主动调用测试

目标：对选定的状态类话题和查询型服务做真实采样 / 调用，验证“可见”是否升级为“可用”。

当前已纳入阶段 2 的能力以 `config/phase2_plan.json` 为准，主要包括：

- IMU
- 触摸
- PMU
- 运动公共状态
- 监控状态
- 屏幕状态
- 手部状态
- 音量 / 静音查询
- 当前运动模式查询
- 当前输入源查询
- 手部类型查询
- 全关节状态查询

产物：

- `inventory/generated/phase2_snapshot.json`
- `inventory/generated/phase2_summary.md`
- 各参与 case 目录下 `phase2.json`

### 阶段 3：有副作用能力测试

目标：验证真正会影响机器人行为的接口。

包括但不限于：

- `PlayTts`
- `SetVolume`
- `SetMute`
- `SetMcAction`
- `SetMcInputSource`
- `SetMcPresetMotion`
- `PlayEmoji`
- `PlayVideo`
- `LedStripCommand`

注意：

- 这类测试不默认自动跑
- 需要明确现场允许、人员到位、机器人状态安全
- 当前实验室只把其中最轻量的 `PlayTts` 作为可选二阶段副作用测试

## 3. 前置条件检查

正式开始前，先做下面这些检查。

### 3.1 网络与登录

在 Windows PowerShell：

```powershell
ping 192.168.88.88
ssh agi@192.168.88.88
```

判定：

- `ping` 不通：先排网络
- `ping` 通但 `ssh` 失败：优先排 SSH 服务、账号、端口、白名单
- `ssh` 成功：继续下一步

### 3.2 机器人环境

登录机器人后检查：

```bash
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
which ros2
ros2 topic list | head
ros2 service list | head
```

判定：

- `which ros2` 没结果：环境未 source
- `ros2` 有但 list 为空：可能 ROS 图未起来，或当前 shell 不在正确运行环境

### 3.3 仓库与脚本

本地仓库根目录应为：

```text
H:\Project\Bot\bot_connect
```

并确认以下入口存在：

- `robot_capability_lab/README.md`
- `robot_capability_lab/TESTING.md`
- `scripts/run_robot_capability_lab.ps1`
- `scripts/run_robot_capability_lab.sh`

## 4. 推荐执行顺序

建议严格按下面顺序走，不要一上来就跑副作用能力。

1. 生成清单与 case
2. 跑阶段 1
3. 看阶段 1 摘要，筛出存在的接口
4. 跑阶段 2
5. 只对明确允许的能力跑副作用测试
6. 回填测试记录
7. 形成结论：可用 / 不可用 / 待复测

## 5. 标准执行流程

### 5.1 本地刷新清单

```powershell
python robot_capability_lab\scripts\build_inventory.py
python robot_capability_lab\scripts\generate_case_folders.py
```

检查输出：

- `robot_capability_lab/inventory/generated/interface_inventory.json`
- `robot_capability_lab/inventory/generated/interface_inventory.md`
- `robot_capability_lab/inventory/generated/project_gap_report.md`

### 5.2 Windows 一键跑阶段 1

```powershell
.\scripts\run_robot_capability_lab.ps1
```

如果需要阶段 1 顺便做低风险话题采样：

```powershell
.\scripts\run_robot_capability_lab.ps1 -SamplePayload
```

### 5.3 Windows 一键跑阶段 2

```powershell
.\scripts\run_robot_capability_lab.ps1 -Phase2
```

如果要一二阶段连续执行：

```powershell
.\scripts\run_robot_capability_lab.ps1 -AllPhases
```

### 5.4 Bash 一键跑阶段 2

```bash
./scripts/run_robot_capability_lab.sh --phase2
```

如果要一二阶段连续执行：

```bash
./scripts/run_robot_capability_lab.sh --all-phases
```

### 5.5 机器人端单独执行

```bash
cd /agibot/data/home/agi/bot_connect
bash robot_capability_lab/scripts/run_probe_remote.sh --phase2
```

### 5.6 可选副作用测试

只有在确认安全后，才允许执行：

```powershell
.\scripts\run_robot_capability_lab.ps1 -Phase2 -AllowSideEffects
```

或：

```bash
./scripts/run_robot_capability_lab.sh --phase2 --allow-side-effects
```

## 6. 结果判定标准

每个接口最终必须落到下面其中一种状态。

### 6.1 可用

定义：

- 接口存在
- 类型匹配
- 能稳定获得 payload / response
- 与文档描述基本一致

建议标记：

- `available`

### 6.2 可见但不可用

定义：

- 接口存在
- 能看到类型或元数据
- 但真实调用 / 采样失败、超时或内容不完整

典型场景：

- 服务能 `type`，但 `call` 连续超时
- 话题能 `info`，但 `echo --once` 无样本

建议标记：

- `visible_but_unusable`

### 6.3 文档存在，真机未证实

定义：

- 知识库有
- 当前真机没发现该接口

建议标记：

- `doc_only`

### 6.4 环境阻塞

定义：

- 机器人或 ROS 环境异常
- 当前轮测试不能得出接口结论

典型场景：

- SSH 登录失败
- `ros2` 环境未加载
- 网络不稳定

建议标记：

- `blocked_by_environment`

### 6.5 有风险未执行

定义：

- 接口已确认存在
- 但由于有副作用，本轮按策略跳过

建议标记：

- `skipped_by_policy`

## 7. 如何判定失败原因

### 7.1 `topic type` 失败

优先判断：

- 话题不存在
- ROS 图未起来
- 当前环境未 source

结论不要直接写“接口不可用”，先写：

- `blocked_by_environment` 或 `doc_only`

### 7.2 `topic info` 有结果，但 `echo --once` 超时

优先判断：

- 当前没有发布者正在发数据
- 该传感器未启用
- 该话题是事件型，不是持续流
- 超时设置过短

这时一般先记：

- `visible_but_unusable`

并备注：

- “需要在传感器活跃时复测”

### 7.3 `service type` 成功，但 `service call` 超时

优先判断：

- 跨板 service 调用偶发超时
- 服务端节点存在但未就绪
- 请求体字段不完整

这时先不要直接写“服务无效”，应：

1. 看 `phase2_probe.py` 的重试记录
2. 对照知识库确认请求字段
3. 再决定是否记为 `visible_but_unusable`

### 7.4 返回成功，但现场没有实际效果

典型于：

- `PlayTts` 返回正常，但机器人没播报
- 表情 / 视频服务返回正常，但屏幕没变化

这类必须补一条人工观察结论：

- “接口回包成功，但现场效果未观察到”

不要直接记成 `available`。

## 8. 人工观察项

下面这些能力不能只看脚本回包，必须人工观察：

- TTS：是否真的播报、是否被更高优先级音频打断
- 表情：屏幕是否真的切换
- 视频：屏幕是否播放成功
- 灯带：灯效是否变化
- 预设动作：是否真的执行动作，是否有安全风险
- 输入源 / 运动模式切换：机器人是否真的进入对应状态

## 9. 测试记录要求

每次正式测试都建议复制一份模板：

- `robot_capability_lab/templates/test_record.md`

记录至少包括：

- 测试时间
- 测试人
- 机器人标识 / IP
- AimDK / ROS 版本
- 跑了哪些阶段
- 哪些接口通过
- 哪些接口失败
- 哪些失败属于环境问题
- 哪些接口建议接入项目

## 10. 常见故障排查

### 10.1 `ssh` 连接被 reset

先检查：

- 机器人 SSH 服务是否开启
- 22 端口是否被限制
- 当前网络是否在同一网段
- 账号 `agi` 是否允许登录

### 10.2 `ros2` 命令不存在

执行：

```bash
source /opt/ros/humble/setup.bash
source /agibot/data/home/agi/aimdk/install/setup.bash
```

### 10.3 一阶段有结果，二阶段大量超时

优先怀疑：

- service 跨板超时
- 当前机器人负载高
- 某些传感器未启用
- 测试时机不对

建议：

- 同一接口复测 2~3 次
- 对照 `phase2_snapshot.json` 里的 attempts

### 10.4 case 目录里没有 `phase2.json`

优先检查：

- 是否真的跑了阶段 2
- 该接口是否被纳入 `config/phase2_plan.json`
- 是否拉回了远端 `cases/` 目录

## 11. 本轮测试结束后的交付物

一次完整测试结束后，至少保留下面这些文件：

- `robot_capability_lab/inventory/generated/runtime_summary.md`
- `robot_capability_lab/inventory/generated/runtime_snapshot.json`
- `robot_capability_lab/inventory/generated/phase2_summary.md`
- `robot_capability_lab/inventory/generated/phase2_snapshot.json`
- `robot_capability_lab/templates/test_record.md` 复制出的本轮记录文件

如果本轮没有跑某个阶段，就明确写明“未执行”。

## 12. 推荐的最终结论格式

建议每轮测试最后输出 3 组清单：

### 12.1 已确认可用

- 可直接作为项目接入候选

### 12.2 已确认存在但仍需复测

- 通常是 `visible_but_unusable`

### 12.3 文档存在但当前真机未证实

- 这类先不要纳入项目排期承诺

---

如果你只执行命令，请看 `README.md`；如果你要做标准化复测和验收，请始终以这份 `TESTING.md` 为准。
