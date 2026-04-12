# 6.2.18 麦克风数据接收

**该示例中用到了mic_receiver** ，通过订阅`/agent/process_audio_output`话题来接收机器人的降噪音频数据，支持内置麦克风和外置麦克风两种音频流，并根据VAD（语音活动检测）状态自动保存完整的语音片段为PCM文件。

**功能特点：**

  * 支持多音频流同时接收（内置麦克风 stream_id=1，外置麦克风 stream_id=2）

  * 基于VAD状态自动检测语音开始、处理中、结束

  * 自动保存完整语音片段为PCM格式文件

  * 按时间戳和音频流分类存储

  * 支持音频时长计算和统计信息输出

**VAD状态说明：**

  * `0`: 无语音

  * `1`: 语音开始

  * `2`: 语音处理中

  * `3`: 语音结束

```cpp
#include <aimdk_msgs/msg/audio_vad_state_type.hpp>
#include <aimdk_msgs/msg/processed_audio_output.hpp>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <rclcpp/rclcpp.hpp>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

namespace fs = std::filesystem;

class AudioSubscriber : public rclcpp::Node {
public:
  AudioSubscriber() : rclcpp::Node("audio_subscriber") {
    // Audio buffers, stored separately by stream_id
    // stream_id -> buffer
    audio_buffers_ = {};
    recording_state_ = {};

    audio_output_dir_ = "audio_recordings";
    fs::create_directories(audio_output_dir_);

    // Note: deep queue to avoid missing data in a burst at start of VAD.
    auto qos = rclcpp::QoS(
        rclcpp::QoSInitialization::from_rmw(rmw_qos_profile_sensor_data));
    qos.keep_last(500).best_effort();

    subscription_ =
        this->create_subscription<aimdk_msgs::msg::ProcessedAudioOutput>(
            "/agent/process_audio_output", qos,
            std::bind(&AudioSubscriber::audio_callback, this,
                      std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(),
                "Starting to subscribe to denoised audio data...");
  }

private:
  void
  audio_callback(const aimdk_msgs::msg::ProcessedAudioOutput::SharedPtr msg) {
    try {
      uint32_t stream_id = msg->stream_id;
      uint8_t vad_state = msg->audio_vad_state.value;
      const std::vector<uint8_t> &audio_data = msg->audio_data;

      static const std::unordered_map<uint8_t, std::string> vad_state_names = {
          {0, "No Speech"},
          {1, "Speech Start"},
          {2, "Speech Processing"},
          {3, "Speech End"}};
      static const std::unordered_map<uint32_t, std::string> stream_names = {
          {1, "Internal Microphone"}, {2, "External Microphone"}};

      RCLCPP_INFO(this->get_logger(),
                  "Audio data received: stream_id=%u, vad_state=%u(%s), "
                  "audio_size=%zu bytes",
                  stream_id, vad_state,
                  vad_state_names.count(vad_state)
                      ? vad_state_names.at(vad_state).c_str()
                      : "Unknown State",
                  audio_data.size());

      handle_vad_state(stream_id, vad_state, audio_data);
    } catch (const std::exception &e) {
      RCLCPP_ERROR(this->get_logger(), "Error processing audio message: %s",
                   e.what());
    }
  }

  void handle_vad_state(uint32_t stream_id, uint8_t vad_state,
                        const std::vector<uint8_t> &audio_data) {
    // Initialize the buffer for this stream_id (if it does not exist)
    if (audio_buffers_.count(stream_id) == 0) {
      audio_buffers_[stream_id] = std::vector<uint8_t>();
      recording_state_[stream_id] = false;
    }

    static const std::unordered_map<uint8_t, std::string> vad_state_names = {
        {0, "No Speech"},
        {1, "Speech Start"},
        {2, "Speech Processing"},
        {3, "Speech End"}};
    static const std::unordered_map<uint32_t, std::string> stream_names = {
        {1, "Internal Microphone"}, {2, "External Microphone"}};

    RCLCPP_INFO(this->get_logger(), "[%s] VAD Atate: %s Audio Data: %zu bytes",
                stream_names.count(stream_id)
                    ? stream_names.at(stream_id).c_str()
                    : ("Unknown Stream " + std::to_string(stream_id)).c_str(),
                vad_state_names.count(vad_state)
                    ? vad_state_names.at(vad_state).c_str()
                    : ("Unknown State" + std::to_string(vad_state)).c_str(),
                audio_data.size());

    // AUDIO_VAD_STATE_BEGIN
    if (vad_state == 1) {
      RCLCPP_INFO(this->get_logger(), "🎤 Speech detected - Start");
      if (recording_state_[stream_id] == false) {
        audio_buffers_[stream_id].clear();
        recording_state_[stream_id] = true;
      }
      if (!audio_data.empty()) {
        audio_buffers_[stream_id].insert(audio_buffers_[stream_id].end(),
                                         audio_data.begin(), audio_data.end());
      }

      // AUDIO_VAD_STATE_PROCESSING
    } else if (vad_state == 2) {
      RCLCPP_INFO(this->get_logger(), "🔄 Speech Processing...");
      if (recording_state_[stream_id] && !audio_data.empty()) {
        audio_buffers_[stream_id].insert(audio_buffers_[stream_id].end(),
                                         audio_data.begin(), audio_data.end());
      }

      // AUDIO_VAD_STATE_END
    } else if (vad_state == 3) {
      RCLCPP_INFO(this->get_logger(), "✅ Speech End");
      if (recording_state_[stream_id] && !audio_data.empty()) {
        audio_buffers_[stream_id].insert(audio_buffers_[stream_id].end(),
                                         audio_data.begin(), audio_data.end());
      }
      if (recording_state_[stream_id] && !audio_buffers_[stream_id].empty()) {
        save_audio_segment(audio_buffers_[stream_id], stream_id);
      }
      recording_state_[stream_id] = false;

      // AUDIO_VAD_STATE_NONE
    } else if (vad_state == 0) {
      if (recording_state_[stream_id]) {
        RCLCPP_INFO(this->get_logger(), "⏹️ Recording state reset");
        recording_state_[stream_id] = false;
      }
    }

    // Output the current buffer status.
    size_t buffer_size = audio_buffers_[stream_id].size();
    bool recording = recording_state_[stream_id];
    RCLCPP_DEBUG(this->get_logger(),
                 "[Stream %u] Buffer size: %zu bytes, Recording state: %s",
                 stream_id, buffer_size, recording ? "true" : "false");
  }

  void save_audio_segment(const std::vector<uint8_t> &audio_data,
                          uint32_t stream_id) {
    if (audio_data.empty())
      return;

    // Get the current timestamp.
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                  now.time_since_epoch()) %
              1000;

    std::ostringstream oss;
    oss << std::put_time(std::localtime(&t), "%Y%m%d_%H%M%S") << "_"
        << std::setw(3) << std::setfill('0') << ms.count();

    // Create a subdirectory by stream_id.
    fs::path stream_dir =
        fs::path(audio_output_dir_) / ("stream_" + std::to_string(stream_id));
    fs::create_directories(stream_dir);

    static const std::unordered_map<uint32_t, std::string> stream_names = {
        {1, "internal_mic"}, {2, "external_mic"}};
    std::string stream_name = stream_names.count(stream_id)
                                  ? stream_names.at(stream_id)
                                  : ("stream_" + std::to_string(stream_id));
    std::string filename = stream_name + "_" + oss.str() + ".pcm";
    fs::path filepath = stream_dir / filename;

    try {
      std::ofstream ofs(filepath, std::ios::binary);
      ofs.write(reinterpret_cast<const char *>(audio_data.data()),
                audio_data.size());
      ofs.close();
      RCLCPP_INFO(this->get_logger(),
                  "Audio segment saved: %s (size: %zu bytes)", filepath.c_str(),
                  audio_data.size());

      // Record audio file duration (assuming 16kHz, 16-bit, mono)
      int sample_rate = 16000;
      int bits_per_sample = 16;
      int channels = 1;
      int bytes_per_sample = bits_per_sample / 8;
      size_t total_samples = audio_data.size() / (bytes_per_sample * channels);
      double duration_seconds =
          static_cast<double>(total_samples) / sample_rate;

      RCLCPP_INFO(this->get_logger(),
                  "Audio duration: %.2f seconds (%zu samples)",
                  duration_seconds, total_samples);
    } catch (const std::exception &e) {
      RCLCPP_ERROR(this->get_logger(), "Failed to save audio file: %s",
                   e.what());
    }
  }

  // Member variables
  std::unordered_map<uint32_t, std::vector<uint8_t>> audio_buffers_;
  std::unordered_map<uint32_t, bool> recording_state_;
  std::string audio_output_dir_;
  rclcpp::Subscription<aimdk_msgs::msg::ProcessedAudioOutput>::SharedPtr
      subscription_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<AudioSubscriber>();
  RCLCPP_INFO(node->get_logger(),
              "Listening for denoised audio data, press Ctrl+C to exit...");
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

**使用说明：**

  1. 运行节点后会自动创建`audio_recordings`目录

  2. 音频文件按stream_id分类存储：

     * `stream_1/`: 内置麦克风音频

     * `stream_2/`: 外置麦克风音频

  3. 文件命名格式：`{stream_name}_{timestamp}.pcm`

  4. 音频格式：16kHz, 16位, 单声道PCM

  5. 可通过以下命令播放保存的PCM文件：

```bash
aplay -r 16000 -f S16_LE -c 1 external_mic_20250909_133649_738.pcm
```

  6. 配合唤醒词触发VAD

**输出示例：**

```cpp
[INFO] 开始订阅降噪音频数据...
[INFO] 收到音频数据: stream_id=2, vad_state=1(语音开始), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音开始 音频数据: 320 bytes
[INFO] 🎤 检测到语音开始
[INFO] 收到音频数据: stream_id=2, vad_state=2(语音处理中), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音处理中 音频数据: 320 bytes
[INFO] 🔄 语音处理中...
[INFO] 收到音频数据: stream_id=2, vad_state=3(语音结束), audio_size=320 bytes
[INFO] [外置麦克风] VAD状态: 语音结束 音频数据: 320 bytes
[INFO] ✅ 语音结束
[INFO] 音频段已保存: audio_recordings/stream_2/external_mic_20250909_133649_738.pcm (大小: 960 bytes)
[INFO] 音频时长: 0.06 秒 (480 样本)
```

_**播放PCM音频文件示例 (Linux下使用aplay命令)**_

假设你已经录制并保存了音频文件 external_mic_20250909_151117_223.pcm， 可以通过如下命令进行播放：

```bash
aplay -r 16000 -f S16_LE -c 1 audio_recordings/stream_2/external_mic_20250909_151117_223.pcm
```

参数说明：

  * -r 16000 # 采样率16kHz

  * -f S16_LE # 16位小端格式

  * -c 1 # 单声道 你也可以用其他音频播放器（如Audacity）以原始PCM格式导入并播放。

注意：如果你保存的是内置麦克风音频，路径应为 audio_recordings/stream_1/internal_mic_xxx.pcm
