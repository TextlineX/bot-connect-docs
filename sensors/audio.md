# 🎤 语音与音频话题

## 📡 话题与类型（实测）
- `/aima/hal/audio/capture` → `aimdk_msgs/msg/AudioCapture`  
  - 发布者：`hal_audio`，QoS：Reliability RELIABLE，Durability VOLATILE  
  - 当前未见实际数据发布（hz/echo 得不到）
- `/aima/hal/audio/playback` → `aimdk_msgs/msg/AudioPlayback`  
  - 订阅者：`hal_audio`，等待上游推送音频播放指令
- `/agent/process_audio_output` → `aimdk_msgs/msg/ProcessedAudioOutput`  
  - 发布者：`aimrt_agent_node`，QoS BEST_EFFORT + TRANSIENT_LOCAL

> 自定义消息在 `ros2 topic echo` 时会提示 invalid type，需安装对应接口包或通过 rosbridge 传输。

## 🔗 WebSocket 远程 ASR 方案（PC 侧识别）
1. 机器人上开启 rosbridge：`sudo apt-get install ros-humble-rosbridge-server`  
   `ros2 launch rosbridge_server rosbridge_websocket_launch.xml` （默认 WS 端口 9090）
2. PC 侧安装依赖：`pip install roslibpy vosk soundfile`，下载 Vosk 16k 模型到如 `/home/you/models/vosk`。
3. 在 PC 侧运行 ASR 脚本（示意，字段名若有差异请用 `ros2 interface show aimdk_msgs/msg/AudioCapture` 对应修改）：
   ```python
   #!/usr/bin/env python3
   import json, roslibpy
   from vosk import Model, KaldiRecognizer

   ROSBRIDGE_IP = '192.168.1.1'
   MODEL_PATH = '/home/you/models/vosk'
   DEFAULT_SR = 16000

   def pcm_from(msg):
       for k in ('data', 'pcm', 'audio'):
           if k in msg:
               return roslibpy.Message.to_binary(msg[k])
       return b''

   model = Model(MODEL_PATH)
   rec = KaldiRecognizer(model, DEFAULT_SR)
   client = roslibpy.Ros(host=ROSBRIDGE_IP, port=9090); client.run()
   pub = roslibpy.Topic(client, '/asr/text', 'std_msgs/String')

   def cb(msg):
       pcm = pcm_from(msg)
       if not pcm: return
       if rec.AcceptWaveform(pcm):
           res = json.loads(rec.Result())
       else:
           res = json.loads(rec.PartialResult())
       text = res.get('text','').strip()
       if text:
           pub.publish({'data': text})
           print('ASR:', text)

   sub = roslibpy.Topic(client, '/aima/hal/audio/capture', 'aimdk_msgs/msg/AudioCapture')
   sub.subscribe(cb)
   client.run_forever()
   ```
4. 机器人侧可直接订阅 `/asr/text` 获取识别结果。

## 🛠️ 播放（TTS → 播放指令）
1. 查看字段：`ros2 interface show aimdk_msgs/msg/AudioPlayback`，确定 PCM 字段名和采样率字段。
2. 上游生成 PCM（如 16k mono），打包为 AudioPlayback 后发布到 `/aima/hal/audio/playback`，`hal_audio` 会播放。

## ❗ 注意
- 确认 PC 与机器人 `ROS_DOMAIN_ID` 一致，多播/防火墙放行；若跨网段，用 CycloneDDS 单播配置指向机器人 IP。
- `audio/capture` 目前未持续发布，需确保 `hal_audio` 正常启用麦克风；可在启动参数或节点参数中查是否有 enable_capture 开关。
