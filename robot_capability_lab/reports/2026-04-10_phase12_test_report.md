# 机器人能力实验室测试报告（2026-04-10）

## 1. 本轮范围

- 测试时间：`2026-04-10`
- 测试阶段：阶段 1（发现性测试）+ 阶段 2（低风险主动调用测试）
- 测试环境：机器人真机，已成功加载 `ROS 2 Humble` 与 `AimDK`
- 副作用测试：未开启

本报告记录的是“本轮真机验证结论”，不是对官方知识库定义的直接改写。

## 2. 总结论

本轮测试已经证明：机器人侧确实开放了一批 ROS 2 话题和服务，系统不是“完全未开放”。

但同时也确认：当前纳入阶段 2 的主动采样与主动查询全部失败，因此这些接口目前只能归类为：

- 已存在但未验证可用
- 或存在运行时限制，暂不能作为项目可用能力直接承诺

因此，本轮文档结论应采用：

- `available`：仅用于已经确认真正确认可用的能力
- `visible_but_unusable`：本轮看得到，但主动采样 / 主动调用失败
- `doc_only`：文档存在，但真机未发现
- `skipped_by_policy`：因风险策略跳过

## 3. 阶段 1 结果

- 探测项总数：`85`
- 发现话题数：`29`
- 发现服务数：`16`

### 3.1 已确认存在的关键服务

- `/aimdk_5Fmsgs/srv/GetAllJointState`
- `/aimdk_5Fmsgs/srv/LedStripCommand`
- `/aimdk_5Fmsgs/srv/GetMcAction`
- `/aimdk_5Fmsgs/srv/SetMcAction`
- `/aimdk_5Fmsgs/srv/SetMcInputSource`
- `/aimdk_5Fmsgs/srv/SetMcPresetMotion`
- `/aimdk_5Fmsgs/srv/GetCurrentInputSource`
- `/aimdk_5Fmsgs/srv/PlayMediaFile`
- `/aimdk_5Fmsgs/srv/PlayEmoji`
- `/aimdk_5Fmsgs/srv/PlayVideo`
- `/aimdk_5Fmsgs/srv/PlayVideoGroup`
- `/aimdk_5Fmsgs/srv/GetMute`
- `/aimdk_5Fmsgs/srv/GetVolume`
- `/aimdk_5Fmsgs/srv/PlayTts`
- `/aimdk_5Fmsgs/srv/SetMute`
- `/aimdk_5Fmsgs/srv/SetVolume`

### 3.2 已确认存在的关键话题类别

- 音频：`/aima/hal/audio/capture`、`/aima/hal/audio/playback`
- IMU：胸部、躯干、雷达 IMU
- 手部：`/aima/hal/joint/hand/command`、`/aima/hal/joint/hand/state`
- 运动状态：`/aima/mc/body_pose`、`/aima/mc/common/state`、`/aima/mc/locomotion/velocity`
- 监控状态：`/aima/hds/alert_code_list`、`/aima/hds/diag_code_list`、`/aima/hds/monitor/info`
- 系统状态：`/aima/sm/system_state`、`/aima/hal/pmu/state`
- 屏幕/表情：`/face_ui_proxy/status`
- 触摸：`/aima/hal/sensor/touch_head`
- 相机：后视 RGB、前双目左右目、前 RGBD 压缩图像

### 3.3 阶段 1 特别说明

- 预设动作在阶段 1 中显示为 `no` 是符合当前探测逻辑的，因为动作本身不是独立 ROS 实体，需通过 `SetMcPresetMotion` 间接验证。
- `/aima/hal/audio/capture` 当前仍应保持 `partial`，因为项目侧只有半接入。
- `/aima/mc/locomotion/velocity` 当前仍应保持 `needs_real_adapter`，因为项目侧尚未真实发布到底层 ROS 接口。

## 4. 阶段 2 结果

- 话题采样成功：`0/8`
- 查询服务成功：`0/6`
- 副作用测试：关闭

### 4.1 话题采样失败项

- `/aima/hal/imu/chest/state`
- `/aima/hal/imu/torso/state`
- `/aima/hal/sensor/touch_head`
- `/aima/hal/pmu/state`
- `/aima/mc/common/state`
- `/aima/hds/monitor/info`
- `/face_ui_proxy/status`
- `/aima/hal/joint/hand/state`

### 4.2 查询服务失败项

- `/aimdk_5Fmsgs/srv/GetVolume`
- `/aimdk_5Fmsgs/srv/GetMute`
- `/aimdk_5Fmsgs/srv/GetMcAction`
- `/aimdk_5Fmsgs/srv/GetCurrentInputSource`
- `/aimdk_5Fmsgs/srv/GetHandType`
- `/aimdk_5Fmsgs/srv/GetAllJointState`

### 4.3 阶段 2 结论

这些接口本轮不能写成“不可用”，但也不能写成“已验证可用”。

更准确的状态是：

- `visible_but_unusable`

原因是：

- 阶段 1 已证明其中大部分接口存在
- 阶段 2 主动采样 / 主动调用全部失败
- 当前还缺少失败原因快照，无法进一步细分为“超时”“无数据”“请求格式问题”还是“跨板调用问题”

## 5. 本轮建议写入文档的结论

### 5.1 可以直接写入实验室文档

- 机器人真机已发现 `29` 个话题与 `16` 个服务
- `PlayTts` 与 `SetMcPresetMotion` 仍是当前项目最明确的核心桥接能力
- 大量感知与状态接口在真机上可见，但本轮主动验证未成功
- 这些接口暂不应承诺为“项目已可稳定使用”

### 5.2 当前不建议直接写入官方知识库原文

- 不建议把失败项直接改成“官方文档错误”
- 不建议把失败项直接改成“该接口不可用”

更合适的做法是：

- 在实验室报告中写“文档存在，真机已发现，但主动验证失败”
- 等拿到 `phase2_snapshot.json` 后，再补失败原因

## 6. 本轮需重点复测项

- `/aimdk_5Fmsgs/srv/GetVolume`
- `/aimdk_5Fmsgs/srv/GetMute`
- `/aimdk_5Fmsgs/srv/GetMcAction`
- `/aimdk_5Fmsgs/srv/GetCurrentInputSource`
- `/aimdk_5Fmsgs/srv/GetAllJointState`
- `/aima/hal/pmu/state`
- `/aima/mc/common/state`
- `/face_ui_proxy/status`
- `/aima/hal/joint/hand/state`

## 7. 特别异常

- `/aimdk_5Fmsgs/srv/GetHandType` 在阶段 1 摘要中显示未发现，但阶段 2 摘要中显示已解析到服务类型。

本项应标注为：

- 真机状态不稳定，需单独复测

## 8. 当前文档落点建议

本轮结果建议作为实验室报告保留，不直接改写官方定义文档。

建议后续基于本报告继续补两类资料：

- 一份带失败原因的补充报告
- 一份“项目可接入优先级清单”

## 9. 本轮最终结论

本轮已经完成了“从文档存在”到“真机存在”的第一步确认。

但对项目接入而言，真正关键的是第二步：主动读 / 主动调是否成功。

当前第二步全部失败，因此现阶段最合理的产品和研发结论是：

- 这些接口很多已经存在
- 但多数尚不能当作稳定可用能力纳入项目承诺
- 后续需要基于失败原因继续复测，而不是直接推翻知识库原文
