<a id="id1"></a>

# 5.2.2 屏幕控制

**屏幕控制接口提供了完整的显示控制能力，包括表情控制、视频播放等功能。通过该接口，开发者可以实现机器人的视觉交互能力。**

<a id="id2"></a>

## 核心功能

  * 多种预设表情播放

  * 自选视频播放

  * 播放列表(待开放)和循环播放

  * 播放优先级控制

<a id="id3"></a>

## 表情播放状态查询话题

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/face_ui_proxy/status` | `FaceEmojiStatus` | Emoji播放状态 | `RELIABLE` | 1Hz  
  
  * `FaceEmojiStatus` ros2-msg @ face_ui/FaceEmojiStatus.msg

```
# 表情状态信息

MessageHeader header             # 消息头
string e_path                    # 表情文件路径
string[] e_path_list             # 当前一组表情的路径列表
uint8 e_id                       # 表情ID
uint8 mode                       # 播放模式 (1:单次, 2:循环)
int32 priority                   # 优先级
uint8 status                     # 当前状态 (0:空闲, 1:开始, 2:运行中, 3:完成, 4:被停止)
float64 time_to_end_ms           # 剩余时长(秒)
```

`status`特别说明:

    * 下列状态edge触发式播报（即只播报1次)

      * 1-开始、3-完成、4-被停止

<a id="id4"></a>

## 表情播放服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/PlayEmoji` | `PlayEmoji` | 播放表情  
  
  * `PlayEmoji` ros2-srv @ face_ui/srv/PlayEmoji.srv

```
# 播放表情
# 服务名称: /aimdk_5Fmsgs/srv/PlayEmoji

# 请求
CommonRequest header # 请求头

uint8 emotion_id  # 表情 id
uint8 mode  # 播放模式枚举 (1:单次, 2:循环)
int32 priority  # 播放优先级

---

# 响应
CommonResponse header  # 响应头

bool success  # 是否控制成功
string message
```

`emotion_id`表情对照表:

<a id="tbl-emotion-id"></a>

表情ID | 表情名称 | 说明  
---|---|---  
1 | 眨眼 | 基础眨眼动作  
10 | 平静-眼睛变化1 | 平静状态眼睛变化  
11 | 平静-眼睛变化2 | 平静状态眼睛变化  
20 | 平静-游戏 | 游戏状态表情  
30-33 | 平静-卖萌 | 卖萌表情系列  
40 | 闭上眼 | 闭眼动作  
50 | 睁开眼 | 睁眼动作  
60 | 无聊 | 无聊表情  
70 | 异常 | 异常状态  
80 | 睡着 | 睡眠状态  
90 | 快乐 | 快乐表情  
100-101 | 加倍开心/狂喜 | 极度开心表情  
110 | 悲伤 | 悲伤表情  
120 | 同情 | 同情表情  
130 | 疑惑 | 疑惑表情  
140 | 震惊 | 震惊表情  
150 | 撒娇 | 撒娇表情  
160 | 严肃 | 严肃表情  
170 | 思考 | 思考表情  
180 | 愤怒 | 愤怒表情  
190 | 加倍愤怒 | 极度愤怒表情  
200 | 崇拜 | 崇拜表情  
210 | 加倍崇拜 | 极度崇拜表情  
220 | 充电 | 充电状态  
  
`priority`优先级机制说明:

    * 本优先级机制涵盖表情播放(PlayEmoji)和稍后描述的视频播放(PlayVideo)

    * 新请求优先级不低于原有请求, 则覆盖原有请求运行

    * 新请求优先级低于原有请求, 则被忽略

<a id="id5"></a>

## 视频播放服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/PlayVideo` | `PlayVideo` | 播放视频  
`/aimdk_5Fmsgs/srv/PlayVideoGroup` | `PlayVideoGroup` | 播放视频列表  
  
  * `PlayVideo` ros2-srv @ face_ui/srv/PlayVideo.srv

```
# 播放视频
# 服务名称: /aimdk_5Fmsgs/srv/PlayVideo

# 请求
CommonRequest header             # 请求头
string video_path                # 视频的绝对路径, 注意文件放在交互计算单元及全员可读权限
uint8 mode                       # 播放模式 (1:单次, 2:循环)
int32 priority                   # 播放优先级

# 响应
CommonResponse header            # 响应头
bool success                     # 是否成功
string message                   # 响应消息
```

<a id="playvideo-notes"></a>

**注意事项** :

    * 视频文件播放默认不播放附带的音频

    * 音视频文件使用绝对路径

    * 音视频文件须放置于交互计算单元(PC3, 10.0.1.42)上, 不在开发计算单元(PC2)上

    * 音视频文件夹及该文件夹所有父目录应当为所有用户可访问读取(建议在/var/tmp/下创建子目录存放)

  * `PlayVideoGroup` ros2-srv @ face_ui/srv/PlayVideoGroup.srv

```
# 播放视频组
# 服务名称: /aimdk_5Fmsgs/srv/PlayVideoGroup

# 请求
CommonRequest header             # 请求头
string[] video_path_list         # 视频组的绝对路径列表, 注意文件放在交互计算单元及全员可读权限
uint8 mode                       # 播放模式 (1:单次, 2:循环)
int32 priority                   # 播放优先级

# 响应
CommonResponse header            # 响应头
bool success                     # 是否成功
string message                   # 响应消息
```

**注意事项** :

    * 同PlayVideo >>

<a id="id6"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ：

    * [表情控制](/official/examples/cpp/emoji)

    * [播放视频](/official/examples/cpp/video-playback)

  * **Python 示例** ：

    * [表情控制](/official/examples/python/emoji)

    * [播放视频](/official/examples/python/video-playback)

<a id="id7"></a>

## 安全注意事项

警告

**显示控制限制**

  * 表情播放会占用显示资源，注意资源管理

  * 视频播放需要确保文件路径正确且可访问

  * 建议合理设置播放优先级，避免冲突

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

**最佳实践**

  * 使用合适的播放模式，避免不必要的循环播放

  * 实现显示状态监控和异常处理

  * 建议实现显示内容队列管理

  * 注意文件路径和格式要求
