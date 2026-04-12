# 6.1.18 麦克风数据接收

**该示例中用到了mic_receiver** ，通过订阅`/agent/process_audio_output`话题来接收机器人的降噪音频数据，支持内置麦克风和外置麦克风两种音频流，并根据VAD（语音活动检测）状态自动保存完整的语音片段为PCM文件。

**功能特点：**

  * 支持多音频流同时接收（内置麦克风 stream_id=1，外置麦克风 stream_id=2）

  * 基于VAD状态自动检测语音开始、处理中、结束

  * 自动保存完整语音片段为PCM格式文件

  * 按时间戳和音频流分类存储

  * 支持音频时长计算和统计信息输出

  * 智能缓冲区管理，避免内存泄漏

  * 完善的错误处理和异常管理

  * 详细的调试日志输出

**VAD状态说明：**

  * `0`: 无语音

  * `1`: 语音开始

  * `2`: 语音处理中

  * `3`: 语音结束

**技术实现：**

  * 支持PCM格式音频文件保存（16kHz, 16位, 单声道）

  * 提供详细的日志输出和状态监控

  * 支持实时音频流处理和文件保存

**应用场景：**

  * 语音识别和语音处理

  * 音频数据采集和分析

  * 实时语音监控

  * 音频质量检测

  * 多麦克风阵列数据处理

```python
#!/usr/bin/env python3
"""
Microphone data receiving example

This example subscribes to the `/agent/process_audio_output` topic to receive the robot's
noise-suppressed audio data. It supports both the built-in microphone and the external
microphone audio streams, and automatically saves complete speech segments as PCM files
based on the VAD (Voice Activity Detection) state.

Features:
- Supports receiving multiple audio streams at the same time (built-in mic stream_id=1, external mic stream_id=2)
- Automatically detects speech start / in-progress / end based on VAD state
- Automatically saves complete speech segments as PCM files
- Stores files categorized by timestamp and audio stream
- Supports audio duration calculation and logging

VAD state description:
- 0: No speech
- 1: Speech start
- 2: Speech in progress
- 3: Speech end
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from aimdk_msgs.msg import ProcessedAudioOutput, AudioVadStateType
import os
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

class AudioSubscriber(Node):
    def __init__(self):
        super().__init__('audio_subscriber')

        # Audio buffers, stored separately by stream_id
        # stream_id -> buffer
        self.audio_buffers: Dict[int, List[bytes]] = defaultdict(list)
        self.recording_state: Dict[int, bool] = defaultdict(bool)

        # Create audio output directory
        self.audio_output_dir = "audio_recordings"
        os.makedirs(self.audio_output_dir, exist_ok=True)

        # VAD state name mapping
        self.vad_state_names = {
            0: "No speech",
            1: "Speech start",
            2: "Speech in progress",
            3: "Speech end"
        }

        # Audio stream name mapping
        self.stream_names = {
            1: "Built-in microphone",
            2: "External microphone"
        }

        # QoS settings
        # Note: deep queue to avoid missing data in a burst at start of VAD.
        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=500,
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )

        # Create subscriber
        self.subscription = self.create_subscription(
            ProcessedAudioOutput,
            '/agent/process_audio_output',
            self.audio_callback,
            qos
        )

        self.get_logger().info("Start subscribing to noise-suppressed audio data...")

    def audio_callback(self, msg: ProcessedAudioOutput):
        """Audio data callback"""
        try:
            stream_id = msg.stream_id
            vad_state = msg.audio_vad_state.value
            audio_data = bytes(msg.audio_data)

            self.get_logger().info(
                f"Received audio data: stream_id={stream_id}, "
                f"vad_state={vad_state}({self.vad_state_names.get(vad_state, 'Unknown state')}), "
                f"audio_size={len(audio_data)} bytes"
            )

            self.handle_vad_state(stream_id, vad_state, audio_data)

        except Exception as e:
            self.get_logger().error(
                f"Error while processing audio message: {str(e)}")

    def handle_vad_state(self, stream_id: int, vad_state: int, audio_data: bytes):
        """Handle VAD state changes"""
        stream_name = self.stream_names.get(
            stream_id, f"Unknown stream {stream_id}")
        vad_name = self.vad_state_names.get(
            vad_state, f"Unknown state {vad_state}")

        self.get_logger().info(
            f"[{stream_name}] VAD state: {vad_name} audio: {len(audio_data)} bytes"
        )

        # Speech start
        if vad_state == 1:
            self.get_logger().info("🎤 Speech start detected")
            if not self.recording_state[stream_id]:
                self.audio_buffers[stream_id].clear()
                self.recording_state[stream_id] = True
            if audio_data:
                self.audio_buffers[stream_id].append(audio_data)

        # Speech in progress
        elif vad_state == 2:
            self.get_logger().info("🔄 Speech in progress...")
            if self.recording_state[stream_id] and audio_data:
                self.audio_buffers[stream_id].append(audio_data)

        # Speech end
        elif vad_state == 3:
            self.get_logger().info("✅ Speech end")
            if self.recording_state[stream_id] and audio_data:
                self.audio_buffers[stream_id].append(audio_data)

            if self.recording_state[stream_id] and self.audio_buffers[stream_id]:
                self.save_audio_segment(stream_id)
            self.recording_state[stream_id] = False

        # No speech
        elif vad_state == 0:
            if self.recording_state[stream_id]:
                self.get_logger().info("⏹️ Reset recording state")
                self.recording_state[stream_id] = False

        # Print current buffer status
        buffer_size = sum(len(chunk)
                          for chunk in self.audio_buffers[stream_id])
        recording = self.recording_state[stream_id]
        self.get_logger().debug(
            f"[Stream {stream_id}] Buffer size: {buffer_size} bytes, recording: {recording}"
        )

    def save_audio_segment(self, stream_id: int):
        """Save audio segment"""
        if not self.audio_buffers[stream_id]:
            return

        # Merge all audio data
        audio_data = b''.join(self.audio_buffers[stream_id])

        # Get current timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # to milliseconds

        # Create subdirectory by stream_id
        stream_dir = os.path.join(self.audio_output_dir, f"stream_{stream_id}")
        os.makedirs(stream_dir, exist_ok=True)

        # Generate filename
        stream_name = "internal_mic" if stream_id == 1 else "external_mic" if stream_id == 2 else f"stream_{stream_id}"
        filename = f"{stream_name}_{timestamp}.pcm"
        filepath = os.path.join(stream_dir, filename)

        try:
            # Save PCM file
            with open(filepath, 'wb') as f:
                f.write(audio_data)

            self.get_logger().info(
                f"Audio segment saved: {filepath} (size: {len(audio_data)} bytes)")

            # Calculate audio duration (assuming 16 kHz, 16-bit, mono)
            sample_rate = 16000
            bits_per_sample = 16
            channels = 1
            bytes_per_sample = bits_per_sample // 8
            total_samples = len(audio_data) // (bytes_per_sample * channels)
            duration_seconds = total_samples / sample_rate

            self.get_logger().info(
                f"Audio duration: {duration_seconds:.2f} s ({total_samples} samples)")

        except Exception as e:
            self.get_logger().error(f"Failed to save audio file: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = AudioSubscriber()

    try:
        node.get_logger().info("Listening to noise-suppressed audio data, press Ctrl+C to exit...")
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Interrupt signal received, exiting...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**使用说明：**

  1. **运行程序** ：

```bash
# 构建Python包
colcon build --packages-select py_examples

# 运行麦克风接收程序, 配合唤醒词触发VAD
ros2 run py_examples mic_receiver
```

  2. **目录结构** ：

     * 运行节点后会自动创建`audio_recordings`目录

     * 音频文件按stream_id分类存储：

       * `stream_1/`: 内置麦克风音频

       * `stream_2/`: 外置麦克风音频

  3. **文件命名格式** ：`{stream_name}_{timestamp}.pcm`

     * `internal_mic_20250909_133649_738.pcm` (内置麦克风)

     * `external_mic_20250909_133650_123.pcm` (外置麦克风)

  4. **音频格式** ：16kHz, 16位, 单声道PCM

  5. **播放保存的PCM文件** ：

```bash
# 播放内置麦克风录音
aplay -r 16000 -f S16_LE -c 1 audio_recordings/stream_1/internal_mic_20250909_133649_738.pcm

# 播放外置麦克风录音
aplay -r 16000 -f S16_LE -c 1 audio_recordings/stream_2/external_mic_20250909_133650_123.pcm
```

  6. **转换为WAV格式** （可选）：

```bash
# 使用ffmpeg转换为WAV格式
ffmpeg -f s16le -ar 16000 -ac 1 -i external_mic_20250909_133649_738.pcm output.wav
```

  7. **程序控制** ：

     * 按 `Ctrl`+`C` 安全退出程序

     * 程序会自动处理音频流的开始和结束

     * 支持同时处理多个音频流

**输出示例：**

**正常启动和运行：**

```python
[INFO] 开始订阅降噪音频数据...
[INFO] 收到音频数据: stream_id=1, vad_state=0(无语音), audio_size=0 bytes
[INFO] [内置麦克风] VAD状态: 无语音 音频数据: 0 bytes
[INFO] 收到音频数据: stream_id=2, vad_state=0(无语音), audio_size=0 bytes
[INFO] [外置麦克风] VAD状态: 无语音 音频数据: 0 bytes
```

**检测到语音开始：**

```python
[INFO] 收到音频数据: stream_id=2, vad_state=1(语音开始), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音开始 音频数据: 320 bytes
[INFO] 🎤 检测到语音开始
```

**语音处理过程：**

```python
[INFO] 收到音频数据: stream_id=2, vad_state=2(语音处理中), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音处理中 音频数据: 320 bytes
[INFO] 🔄 语音处理中...
[INFO] 收到音频数据: stream_id=2, vad_state=2(语音处理中), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音处理中 音频数据: 320 bytes
[INFO] 🔄 语音处理中...
```

**语音结束和保存：**

```python
[INFO] 收到音频数据: stream_id=2, vad_state=3(语音结束), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音结束 音频数据: 320 bytes
[INFO] ✅ 语音结束
[INFO] 音频段已保存: audio_recordings/stream_2/external_mic_20250909_133649_738.pcm (大小: 960 bytes)
[INFO] 音频时长: 0.06 秒 (480 样本)
```

**多音频流同时处理：**

```python
[INFO] 收到音频数据: stream_id=1, vad_state=1(语音开始), audio_size=320 bytes
[INFO] [内置麦克风] VAD状态: 语音开始 音频数据: 320 bytes
[INFO] 🎤 检测到语音开始
[INFO] 收到音频数据: stream_id=2, vad_state=1(语音开始), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音开始 音频数据: 320 bytes
[INFO] 🎤 检测到语音开始
```

**程序退出：**

```python
^C[INFO] 接收到中断信号，正在退出...
[INFO] 程序已安全退出
```

**注意事项：**

  * 程序支持同时处理多个音频流（内置和外置麦克风）

  * 每个音频流都有独立的缓冲区和录音状态

  * 音频文件会自动按时间戳和音频流分类保存

  * 程序具有完善的错误处理机制，确保稳定运行
