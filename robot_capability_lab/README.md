# 机器人能力探测实验室

这个目录专门用来系统化验证机器人到底开放了哪些能力、每个 ROS 2 话题/服务到底能拿到什么数据、以及当前项目实际桥接到了哪些能力。

如果你要做正式测试、交接给别人复测，除了本文件，还请直接看：

- `robot_capability_lab/TESTING.md`
- `robot_capability_lab/templates/test_record.md`
- `robot_capability_lab/reports/2026-04-10_phase12_test_report.md`

## 先说结论

按当前项目代码和知识库对照，现状大致是这样：

- 已有真实 ROS2 桥接：
  - `PlayTts` 服务
  - `SetMcPresetMotion` 服务
- 只有“半桥接”或“占位”的能力：
  - 运动控制：前端有 `cmd_vel`，但当前 `master/handlers/motion.py` 只是更新本地 `RobotSDK` 状态，没有真正向 `/aima/mc/locomotion/velocity` 发布
  - 音频识别：当前走的是前端上传音频到 PC 本地 ASR，不是直接订阅机器人 MIC/VAD 话题
- 知识库里明确存在但项目还没系统接入的能力：
  - 相机
  - IMU
  - 触摸
  - 激光雷达
  - PMU / 电池
  - 屏幕 / 表情 / 视频
  - 灯带
  - 音量 / 静音
  - 运动模式查询 / 切换
  - 关节 / 末端执行器

所以这个目录的目标不是“猜”，而是把每个接口都落成可追踪的测试项。

## 目录结构

```text
robot_capability_lab/
├─ README.md
├─ config/
│  ├─ project_bindings.json
│  └─ phase2_plan.json
├─ inventory/
│  └─ generated/
├─ cases/
│  ├─ topics/
│  ├─ services/
│  └─ actions/
└─ scripts/
   ├─ build_inventory.py
   ├─ generate_case_folders.py
   ├─ phase2_probe.py
   ├─ ros_probe.py
   └─ run_probe_remote.sh
```

## 工作流

### 1. 重新生成知识库接口清单

在仓库根目录运行：

```powershell
python robot_capability_lab\scripts\build_inventory.py
```

它会做三件事：

- 扫描 `知识库/` 里的官方文档和整理文档
- 抽取话题、服务、预设动作
- 对照 `robot_capability_lab/config/project_bindings.json` 生成项目覆盖报告

输出文件：

- `robot_capability_lab/inventory/generated/interface_inventory.json`
- `robot_capability_lab/inventory/generated/interface_inventory.md`
- `robot_capability_lab/inventory/generated/project_gap_report.md`

### 2. 为每个接口生成独立测试目录

```powershell
python robot_capability_lab\scripts\generate_case_folders.py
```

生成结果示例：

- `robot_capability_lab/cases/topics/aima__hal__audio__capture/`
- `robot_capability_lab/cases/topics/aima__hal__sensor__rgbd_head_front__rgb_image__compressed/`
- `robot_capability_lab/cases/services/aimdk_5Fmsgs__srv__PlayTts/`

每个目录里会带：

- `case.json`：结构化元信息
- `README.md`：该接口该怎么测、测什么、哪些命令可直接跑

### 3. 在机器人环境做真机探测

在已经 `source` 好 ROS2 / AimDK 环境的机器上运行：

```bash
python robot_capability_lab/scripts/ros_probe.py
```

这个脚本默认只做“安全探测”：

- 会查话题/服务是否存在
- 会记录类型、`info -v`、`interface show`
- 会对可安全采样的话题做 `echo --once`
- 对高带宽话题默认不直接 dump 全量 payload
- 默认不会主动调用服务

输出：

- `robot_capability_lab/inventory/generated/runtime_snapshot.json`
- `robot_capability_lab/inventory/generated/runtime_summary.md`
- 每个 case 目录下的 `runtime.json`

### 3.5 二阶段低风险主动测试

二阶段不是“盲调”，而是在一阶段发现接口确实存在以后，继续做低风险主动查询：

- 对选定状态类话题做 `echo --once`
- 对查询型服务做真实 `ros2 service call`
- 默认不执行有副作用的服务
- 副作用测试只有显式开启后才运行

机器人端直接运行：

```bash
python robot_capability_lab/scripts/phase2_probe.py
```

如果要允许低优先级 TTS 主动调用测试：

```bash
python robot_capability_lab/scripts/phase2_probe.py --allow-side-effects
```

输出：

- `robot_capability_lab/inventory/generated/phase2_snapshot.json`
- `robot_capability_lab/inventory/generated/phase2_summary.md`
- 每个参与二阶段的 case 目录下 `phase2.json`

### 4. 先同步到机器人

如果你要先把这个实验室目录推到机器人，可以直接运行：

```bash
./scripts/sync_robot_capability_lab.sh
```

默认会同步到：

```text
agi@192.168.88.88:/agibot/data/home/agi/bot_connect/robot_capability_lab
```

也支持覆盖主机和远端基目录：

```bash
./scripts/sync_robot_capability_lab.sh agi@192.168.88.88 /agibot/data/home/agi/bot_connect
```

### 5. 一键同步并测试

如果你希望本机直接一键完成：

- 本地刷新接口清单
- 同步到机器人
- 机器人执行一阶段/二阶段探测
- 拉回探测摘要和 case 结果

可以用：

```bash
./scripts/run_robot_capability_lab.sh
```

如果在 Windows PowerShell：

```powershell
.\scripts\run_robot_capability_lab.ps1
```

如果你要对低风险话题顺便做一次 `echo --once` 采样：

```bash
SAMPLE_PAYLOAD=1 ./scripts/run_robot_capability_lab.sh
```

```powershell
.\scripts\run_robot_capability_lab.ps1 -SamplePayload
```

如果你要直接跑二阶段：

```bash
./scripts/run_robot_capability_lab.sh --phase2
```

```powershell
.\scripts\run_robot_capability_lab.ps1 -Phase2
```

如果你要一键跑完一阶段和二阶段：

```bash
./scripts/run_robot_capability_lab.sh --all-phases
```

```powershell
.\scripts\run_robot_capability_lab.ps1 -AllPhases
```

如果你确认现场允许测试低优先级 TTS 主动调用：

```bash
./scripts/run_robot_capability_lab.sh --phase2 --allow-side-effects
```

```powershell
.\scripts\run_robot_capability_lab.ps1 -Phase2 -AllowSideEffects
```

机器人端也可以单独执行：

```bash
cd /agibot/data/home/agi/bot_connect
bash robot_capability_lab/scripts/run_probe_remote.sh
```

只跑二阶段：

```bash
cd /agibot/data/home/agi/bot_connect
bash robot_capability_lab/scripts/run_probe_remote.sh --phase2
```

一二阶段一起跑：

```bash
cd /agibot/data/home/agi/bot_connect
bash robot_capability_lab/scripts/run_probe_remote.sh --all-phases
```

## 测试原则

- 每个话题都要有独立 case 目录，不能只靠总表口头记录
- 文档说“待开放 / 待发布”的接口，也要保留 case，但结论要明确写成“文档存在，真机待证实”
- 高带宽接口优先验证：
  - 能否发现
  - 类型是否匹配
  - 频率是否稳定
  - 是否能安全拿到样本
- 服务默认只验证“是否存在 + 调用格式”，真正调用前要先确认安全
- 二阶段默认只做低风险查询服务；像运动切换、表情播放、灯带、主动动作这类有明显副作用的能力，不默认自动执行
- 即使是查询服务，跨板通信也可能偶发超时，所以二阶段脚本内置了快速重试

## 建议执行顺序

优先把这些先跑掉：

1. 音频：`/aima/hal/audio/capture`、`/agent/process_audio_output`
2. 相机：前双目、前 RGBD、后视 RGB
3. 触摸：`/aima/hal/sensor/touch_head`
4. IMU：胸部、躯干、雷达 IMU、RGBD IMU
5. Lidar：点云和雷达 IMU
6. PMU：`/aima/hal/pmu/state`
7. 屏幕 / 表情服务
8. 音量 / 静音 / TTS
9. 运动模式 / locomotion / preset motion

## 你后面怎么用这个目录

以后我们只要做两件事：

- 新发现一个真实可用接口，就把 case 的 `runtime.json` 和结论补齐
- 新做一个项目桥接，就更新 `project_bindings.json`
- 二阶段已覆盖的接口，继续把 `phase2.json` 留在对应 case 目录里

这样知识库、项目实现、真机结果就能始终对齐，而不是再靠脑子记。
