# 🔋 电池 BMS

## 📡 基础通信参数
- 话题：`/aima/battery_state/pb_3Aaimdk_2Eprotocol_2EBmsState`
- 类型：`ros2_plugin_proto/msg/RosMsgWrapper`（封装 Protobuf）

## 📊 运行特性
- 本次未测得频率，属于低频状态类；需在电池活跃发布时再确认 Hz。

## ⚠️ 使用提示
1. 消息被 RosMsgWrapper 包裹，订阅后需按协议解包 Protobuf 原始 BmsState。
2. 若已有上层订阅假设原生类型，需要更新解析逻辑或添加转换节点。
