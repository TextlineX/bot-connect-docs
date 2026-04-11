# 🏥 系统监控与诊断

## 📡 基础通信参数（实测类型）
- `/aima/hds/monitor/info` → `aimdk_msgs/msg/HdsMonitor`
- `/aima/hds/alert_code_list` → `aimdk_msgs/msg/AlertCodeArray`
- `/aima/hds/diag_code_list` → `aimdk_msgs/msg/DiagnosticInfoArray`
- `/aima/sm/system_state` → `aimdk_msgs/msg/SmSystemState`
- QoS：未见特殊设置，默认可用。

## 📊 运行特性
- 本次未测得频率，多为事件/低频状态类消息；需在故障/告警场景复测 Hz。

## ⚠️ 使用提示
1. 上层若仍按 aima_msgs 解析，需要同步更新依赖或增加类型转换。
2. 告警/诊断列表建议与 PMU、电池状态联合使用，形成完整健康状态视图。
