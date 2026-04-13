# 6.1.16 媒体文件播放

**该示例中用到了play_media** ，通过该节点可实现播放指定的媒体文件（如音频文件），支持WAV、MP3等格式的音频文件播放。

**功能特点：**

  * 支持多种音频格式播放（WAV、MP3等）

  * 支持优先级控制，可设置播放优先级

  * 支持打断机制，可中断当前播放

  * 支持自定义文件路径和播放参数

  * 提供完整的错误处理和状态反馈

**技术实现：**

  * 使用PlayMediaFile服务进行媒体文件播放

  * 支持优先级级别设置（0-99）

  * 支持中断控制（is_interrupted参数）

  * 提供详细的播放状态反馈

  * 兼容不同的响应字段格式

**应用场景：**

  * 音频文件播放和媒体控制

  * 语音提示和音效播放

  * 多媒体应用开发

  * 机器人交互音频反馈

注意

**⚠️ 请注意！交互计算单元(PC3)独立于二开程序所在的开发计算单元(PC2), 音视频文件务必存入交互计算单元(IP: 10.0.1.42)。**   
**⚠️ 音视频文件夹及该文件夹所有父目录应当为所有用户可访问读取(建议在/var/tmp/下创建子目录存放)**

```python
#!/usr/bin/env python3

import sys
import rclpy
import rclpy.logging
from rclpy.node import Node

from aimdk_msgs.srv import PlayMediaFile
from aimdk_msgs.msg import TtsPriorityLevel

class PlayMediaClient(Node):
    def __init__(self):
        super().__init__('play_media_client')
        self.client = self.create_client(
            PlayMediaFile, '/aimdk_5Fmsgs/srv/PlayMediaFile')
        self.get_logger().info('✅ PlayMedia client node created.')

        # Wait for the service to become available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('⏳ Service unavailable, waiting...')

        self.get_logger().info('🟢 Service available, ready to send request.')

    def send_request(self, media_path):
        req = PlayMediaFile.Request()

        req.media_file_req.file_name = media_path
        req.media_file_req.domain = 'demo_client'       # required: caller domain
        req.media_file_req.trace_id = 'demo'            # optional
        req.media_file_req.is_interrupted = True        # interrupt same-priority
        req.media_file_req.priority_weight = 0          # optional: 0~99
        req.media_file_req.priority_level.value = TtsPriorityLevel.INTERACTION_L6

        self.get_logger().info(
            f'📨 Sending request to play media: {media_path}')
        for i in range(8):
            req.header.header.stamp = self.get_clock().now().to_msg()
            future = self.client.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=0.25)

            if future.done():
                break

            # retry as remote peer is NOT handled well by ROS
            self.get_logger().info(f'trying ... [{i}]')

        resp = future.result()
        if resp is None:
            self.get_logger().error('❌ Service call not completed or timed out.')
            return False

        if resp.tts_resp.is_success:
            self.get_logger().info('✅ Request to play media file recorded successfully.')
            return True
        else:
            self.get_logger().error('❌ Failed to record play-media request.')
            return False

def main(args=None):
    rclpy.init(args=args)
    node = None

    default_media = '/agibot/data/var/interaction/tts_cache/normal/demo.wav'
    try:
        if len(sys.argv) > 1:
            media_path = sys.argv[1]
        else:
            media_path = input(
                f'Enter media file path to play (default: {default_media}): ').strip()
            if not media_path:
                media_path = default_media

        node = PlayMediaClient()
        node.send_request(media_path)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        rclpy.logging.get_logger('main').error(
            f'Program exited with exception: {e}')

    if node:
        node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**使用说明：**

```bash
# 播放默认音频文件
ros2 run py_examples play_media

# 播放指定音频文件
# 注意替换/path/to/your/audio_file.wav为交互板上实际文件路径
ros2 run py_examples play_media /path/to/your/audio_file.wav

# 播放TTS缓存文件
ros2 run py_examples play_media /agibot/data/var/interaction/tts_cache/normal/demo.wav
```

**输出示例：**

```python
[INFO] [play_media_file_client_min]: 等待服务: /aimdk_5Fmsgs/srv/PlayMediaFile
[INFO] [play_media_file_client_min]: ✅ 媒体文件播放请求成功
```

**注意事项：**

  * 确保音频文件路径正确且文件存在

  * 支持的文件格式：WAV、MP3等

  * 优先级设置影响播放队列顺序

  * 打断功能可中断当前播放的音频

  * 程序具有完善的异常处理机制
