# 官方文档精简导览

面向 X2 机器人官方文档的简化索引，按主题归档并去掉冗余入口，方便在知识库中快速定位。

## 1. 产品与硬件
- 机器人概览与部件: `1_about_agibot_X2/part_name.md`
- 关键参数: `1_about_agibot_X2/robot_specifications.md`
- 计算单元: `1_about_agibot_X2/onboard_computer.md`
- 传感器能力与视场: `1_about_agibot_X2/sensor_fov.md`
- 关节活动范围: `1_about_agibot_X2/joint_name_and_limit.md`
- 坐标系说明: `1_about_agibot_X2/coordinate_system.md`
- 调试与二开接口总览: `1_about_agibot_X2/SDK_interface.md`

## 2. 操作与连接
- 开机与站立流程: `2_operation_guide/start_up_guide.md`
- 手机 App 连接: `2_operation_guide/robot_connection.md`
- 遥控手柄连接: `2_operation_guide/remote_controller.md`
- 关机步骤: `2_operation_guide/shutdown.md`

## 3. SDK 获取与快速开始
- 获取 SDK: `3_get_sdk/index.md`
- 准备与依赖: `4_quick_start/prerequisites.md`
- 运行示例与代码样例: `4_quick_start/run_example.md`, `4_quick_start/code_sample.md`

## 4. 接口参考
- 控制接口（模式切换、关节、行走、末端、预置动作等）: `5_interface/control_mod/*.md`
- 感知接口（视觉、SLAM）: `5_interface/perception/*.md`
- HAL 与电源管理: `5_interface/hal/*.md`
- 交互接口（灯、屏、语音）: `5_interface/interactor/*.md`
- 故障与 sudo 工具（FASM）: `5_interface/FASM/*.md`

## 5. 示例与 FAQ
- Python 示例:
  - 总文档: `6_examples/python/Python.md`
  - 拆分小节索引: `6_examples/python/split/index.md`（每个示例独立成文档）
- C++ 示例:
  - 总文档: `6_examples/cpp/Cpp.md`
  - 拆分小节索引: `6_examples/cpp/split/index.md`
- 常见问题: `7_faq/index.md`, 临时问题收集: `7_faq/temp_works.md`

## 6. 建议忽略的冗余文件
- 自动生成的站点导航/索引：`index.md`, `genindex.md`, `search.md`
- 版本附注与反馈入口：`changelog.md`, `end_notes.md`, `feedback.md`

> 以上文件保留以便追溯，但在知识库检索时可过滤掉“建议忽略”列表，避免重复命中。
