# topic 测试项

- 名称: `/agent/process_audio_output`
- 分类: `audio`
- 类型: `aimdk_msgs/msg/ProcessedAudioOutput`
- 文档状态: `实测`
- 项目状态: `not_connected`

## 文档来源

- `知识库/02_传感器硬件抽象层/语音音频.md` | 📡 话题与类型（实测）
- `知识库/官方/5_interface/interactor/voice.md` | MIC音频流采集话题

## 推荐命令

```bash
ros2 topic info /agent/process_audio_output -v
ros2 topic type /agent/process_audio_output
ros2 interface show aimdk_msgs/msg/ProcessedAudioOutput
# 高带宽话题，默认先跑: ros2 topic hz /agent/process_audio_output
# 若确认安全，再手工采样: ros2 topic echo /agent/process_audio_output --once
```

## 测试记录

- 首次验证时间: 
- 机器人环境: 
- 是否存在: 
- 实际类型: 
- QoS / 频率: 
- 样本是否拿到: 
- 结论: 
- 备注: 
