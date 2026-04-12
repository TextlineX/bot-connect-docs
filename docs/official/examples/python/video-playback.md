# 6.1.15 播放视频

**该示例中用到了play_video** ，在运行节点程序前，需要先将视频上传到机器人的**交互计算单元(PC3)**上（用户可在其上创建一个用来存储视频的目录,如/var/tmp/videos/），然后将节点程序中的`video_path`改为需要播放视频的路径。

注意

**⚠️ 请注意！交互计算单元(PC3)独立于二开程序所在的开发计算单元(PC2), 音视频文件务必存入交互计算单元(IP: 10.0.1.42)。**   
**⚠️ 音视频文件夹及该文件夹所有父目录应当为所有用户可访问读取(建议在/var/tmp/下创建子目录存放)**

**功能说明**  
通过调用`PlayVideo`服务，可以让机器人在屏幕上播放指定路径的视频文件。请确保视频文件已上传到交互计算单元，否则播放会失败。

```python
#!/usr/bin/env python3

import rclpy
import rclpy.logging
from rclpy.node import Node

from aimdk_msgs.srv import PlayVideo

class PlayVideoClient(Node):
    def __init__(self):
        super().__init__('play_video_client')
        self.client = self.create_client(
            PlayVideo, '/face_ui_proxy/play_video')
        self.get_logger().info('✅ PlayVideo client node created.')

        # Wait for the service to become available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('⏳ Service unavailable, waiting...')

        self.get_logger().info('🟢 Service available, ready to send request.')

    def send_request(self, video_path, mode, priority):
        req = PlayVideo.Request()

        req.video_path = video_path
        req.mode = mode
        req.priority = priority

        # async call
        self.get_logger().info(
            f'📨 Sending request to play video: mode={mode} video={video_path}')
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

        if resp.success:
            self.get_logger().info(
                f'✅ Request to play video recorded successfully: {resp.message}')
            return True
        else:
            self.get_logger().error(
                f'❌ Failed to record play-video request: {resp.message}')
            return False

def main(args=None):
    rclpy.init(args=args)
    node = None

    try:
        # video path and priority can be customized
        video_path = "/agibot/data/home/agi/zhiyuan.mp4"
        priority = 5
        # input play mode
        mode = int(input("Enter video play mode (1: play once, 2: loop): "))
        if mode not in (1, 2):
            raise ValueError(f'invalid mode {mode}')

        node = PlayVideoClient()
        node.send_request(video_path, mode, priority)
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
