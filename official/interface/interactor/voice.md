<a id="id1"></a>

# 5.2.1 语音控制

**语音控制接口提供了完整的语音交互能力，包括语音合成、语音识别、音频降噪、音频播放和音量控制等功能。**

<a id="id2"></a>

## 核心特性

<a id="tts"></a>

### 语音合成 (TTS)

  * **文本转语音** ：将文本转换为自然语音

  * **多语言支持** ：支持中文、英文等多种语言

  * **情感语音** ：支持不同情感风格的语音合成

  * **优先级管理** ：支持多级优先级控制

<a id="asr"></a>

### 语音识别 (ASR)（待开放）

  * **实时识别** ：支持实时语音识别

  * **多语言识别** ：支持中文、英文等多种语言

  * **音频流处理** ：支持音频流实时处理

<a id="id3"></a>

### 音频处理

  * **实时降噪** ：支持实时音频降噪处理

  * **语音活动检测** ：支持VAD（Voice Activity Detection）

  * **流式传输** ：支持降噪后音频流式传输

<a id="id4"></a>

### 音频播放

  * **音频流播放** ：支持音频数据流播放

  * **优先级控制** ：支持播放优先级管理

  * **格式支持** ：支持多种音频格式

<a id="id5"></a>

### 音量控制

  * **音量调节** ：支持系统音量调节

  * **静音控制** ：支持静音/取消静音

  * **音量查询** ：支持当前音量查询

<a id="id6"></a>

## 音量控制服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/GetVolume` | `GetVolume` | 查询音量  
`/aimdk_5Fmsgs/srv/SetVolume` | `SetVolume` | 设置音量  
`/aimdk_5Fmsgs/srv/GetMute` | `GetMute` | 查询静音  
`/aimdk_5Fmsgs/srv/SetMute` | `SetMute` | 设置静音  
  
<a id="def-rossrv-getvolume"></a>

  * `GetVolume` ros2-srv @ /hal/audio/srv/GetVolume.srv

```
# 获取音量
# 服务名称: /aimdk_5Fmsgs/srv/GetVolume

# 请求
CommonRequest request            # 请求头

---

# 响应
CommonResponse reponse           # 响应头
uint32 audio_volume              # 当前音量 (0-100)
```

<a id="def-rossrv-setvolume"></a>

  * `SetVolume` ros2-srv @ /hal/audio/srv/SetVolume.srv

```
# 设置音量
# 服务名称: /aimdk_5Fmsgs/srv/SetVolume

# 请求
CommonRequest request            # 请求头
uint32 audio_volume              # 音量值 (0-100)

---

# 响应
CommonResponse reponse           # 响应头
uint32 audio_volume              # 当前音量 (0-100)
```

<a id="def-rossrv-getmute"></a>

  * `GetMute` ros2-srv @ /hal/audio/srv/GetMute.srv

```
# 获取静音状态
# 服务名称: /aimdk_5Fmsgs/srv/GetMute

# 请求
CommonRequest request            # 请求头

---

# 响应
CommonResponse reponse           # 响应头
bool is_mute                     # 当前静音状态
```

<a id="def-rossrv-setmute"></a>

  * `SetMute` ros2-srv @ /hal/audio/srv/SetMute.srv

```
# 设置静音
# 服务名称: /aimdk_5Fmsgs/srv/SetMute

# 请求
CommonRequest request            # 请求头
bool is_mute                     # 静音状态

---

# 响应
CommonResponse reponse           # 响应头
bool is_mute                     # 当前静音状态
```

<a id="id7"></a>

## 语音合成服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/PlayTts` | `PlayTts` | 语音合成(文字转语音)播放  
  
  * `PlayTts` ros2-srv @ interaction/srv/PlayTts.srv

```
# 语音合成播放
# 服务名称: /aimdk_5Fmsgs/srv/PlayTts

# 请求
CommonRequest header
PlayTtsRequest tts_req #内嵌Request msg

---

# 响应
CommonResponse header
PlayTtsResponse tts_resp  #内嵌Response msg
```

其中

    * `PlayTtsRequest` ros2-msg @ interaction/msg/PlayTtsRequest.msg

```
# 内嵌Request msg

string text                      # 文本内容
TtsPriorityLevel priority_level  # 优先级级别 (见下方TtsPriorityLevel说明)
uint32 priority_weight           # 优先级权重 (0-99)
string domain                    # 调用方来源
string trace_id                  # 请求追踪ID
bool is_interrupted              # 是否打断同等优先级播报(不打断时进播放队列)
```

      * `TtsPriorityLevel` ros2-msg @ interaction/msg/TtsPriorityLevel.msg

```
# TTS优先级级别
uint8 value                      # 优先级值
```

`TtsPriorityLevel`可用级别:

<a id="tbl-tts-prioritylevel"></a>

级别 | 数值 | 说明 | 使用场景  
---|---|---|---  
紧急安全层(SAFETY_L10) | 10 | 最高优先级 | 安全警告、紧急通知  
危险预警层(WARNING_L8) | 8 | 高优先级 | 危险提醒、警告信息  
系统提示层(SYSTEM_L7) | 7 | 中高优先级 | 系统语音播报  
交互响应层(INTERACTION_L6) | 6 | 中优先级 | 用户交互、对话响应  
任务执行层(MISSION_L4) | 4 | 中低优先级 | 任务执行、状态播报  
主动服务层(SERVICE_L2) | 2 | 低优先级 | 主动服务、提醒  
后台服务层(BACKGROUND_L1) | 1 | 最低优先级 | 后台服务、日志  
  
声音播放优先级机制说明:

        * 本优先级体系涵盖语音合成播放(PlayTts)与稍后描述的音频文件播放(PlayMediaFile)

        * 高优先级播报打断低优先级播报

        * 同优先级播报根据`priority_weight`和`is_interrupted`参数决定

        * 打断时当前播放队列将被清空

        * 紧急安全层优先级最高，不被任何其他优先级打断

<a id="def-rosmsg-playttsresponse"></a>

    * `PlayTtsResponse` ros2-msg @ interaction/msg/PlayTtsResponse.msg

```
# 内嵌Response msg
string text                      # 响应文本
TtsPriorityLevel priority_level  # 优先级级别
uint32 priority_weight           # 优先级权重
string domain                    # 调用方来源
string trace_id                  # 请求追踪ID
bool is_success                  # 是否成功
string error_message             # 错误信息
uint32 estimated_duration        # 预计耗时(毫秒)
```

<a id="id8"></a>

## 音频文件播放服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/PlayMediaFile` | `PlayMediaFile` | 音频文件播放  
  
  * `PlayMediaFile` ros2-srv @ interaction/srv/PlayMediaFile.srv

```
# 播放音频文件
# 服务名称: /aimdk_5Fmsgs/srv/PlayMediaFile

# 请求
CommonRequest header
PlayMediaFileRequest media_file_req

---

# 响应
CommonResponse header
PlayTtsResponse tts_resp  #复用PlayTtsResponse
```

    * `PlayMediaFileRequest` ros2-msg @ interaction/msg/PlayMediaFileRequest.msg

```
# 内嵌Request msg

string file_name  # 音频文件的绝对路径, 注意文件放在交互计算单元及全员可读权限
uint32 sample_rate  # 暂不使用。默认16k1ch
TtsPriorityLevel priority_level  # 推荐默认INTERACTION_L6
uint32 priority_weight  # 权重(0-99)
string domain  # 调用方来源
string trace_id  # 请求追踪ID
bool is_interrupted # 是否打断同等优先级播报(不打断时进播放队列)
```

其中`priority_level`取值参考声音播放优先级表

    * `PlayTtsResponse`如前所述

注意事项:

    * 音频文件需要是PCM编码的原始文件(要求后缀.pcm)或封装该pcm的WAV文件(要求后缀.wav)

    * 音频对应采样率16kHz, 位深16bit, 单声道

    * 音视频文件使用绝对路径

    * 音视频文件须放置于交互计算单元(PC3, 10.0.1.42)上, 不在开发计算单元(PC2)上

    * 音视频文件夹及该文件夹所有父目录应当为所有用户可访问读取(建议在/var/tmp/下创建子目录存放)

<a id="mic-receiver-vad"></a>

## MIC音频流采集话题

支持获取实时降噪后的语音活动检测(VAD, Voice Activity Detection)事件及相应音频流

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/agent/process_audio_output` | `ProcessedAudioOutput` | VAD音频采集 | - | 触发式, 识别到语言后先将识别阶段堆积的数据极速发出, 后续约25Hz  
  
  * `ProcessedAudioOutput` ros2-msg @ interaction/msg/ProcessedAudioOutput.msg

```
MessageHeader header  # 消息头

uint32 stream_id  # 音频流id (1:本体mic, 2:外置mic)
AudioVadStateType audio_vad_state  # VAD状态 (0: 无语言, 1: 语言开始, 2:语言处理中, 3:语言结束)
uint8[] audio_data # 语音数据 (PCM编码, 16kHz/16bit/1ch)
```

**注意音频流格式** :

  * 采样率: 16kHz

  * 位深: 16bit

  * 声道: 单声道

  * 编码: PCM

注意

VAD 需要配合唤醒词使用(v0.9+), 用法如下:

  * 原生的智元交互保持开启时, 唤醒词仅短时激活VAD检测, 该时段的语言触发VAD音频流

  * 智元交互切换到[`only_voice`模式](/official/faq/temp_works#agent-only-voice)时, 首次唤醒词已长期激活VAD检测，后续只需有语言即可触发VAD音频流

<a id="id9"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ：

    * [TTS (文字转语音)](/official/examples/cpp/tts)

    * [媒体文件播放](/official/examples/cpp/media-playback)

    * [麦克风数据接收](/official/examples/cpp/microphone)

  * **Python 示例** ：

    * [TTS (文字转语音)](/official/examples/cpp/tts)

    * [媒体文件播放](/official/examples/cpp/media-playback)

    * [麦克风数据接收](/official/examples/cpp/microphone)

<a id="id10"></a>

## 安全注意事项

警告

**语音播放限制**

  * 语音合成服务有优先级限制，避免同时播放多个语音

  * 高优先级语音会打断低优先级语音，请合理设置优先级

  * 建议在语音播放前检查当前播放状态

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

**最佳实践**

  * 使用合适的优先级级别，避免影响重要信息播报

  * 实现语音播放状态监控和异常处理

  * 建议实现语音播放队列管理

  * 注意音频格式和采样率要求

  * VAD 接收队列深度应充分预留

  * VAD 不要忘记使用唤醒词
