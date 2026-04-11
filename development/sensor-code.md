# 传感器编程规范

在进行二次开发编写订阅传感器数据的节点时，必须遵循以下规则：

## 1. 高频数据订阅：必须降频处理
IMU 等高频话题 (500Hz) 的回调函数如果不加限制，会迅速占满 CPU 资源。
- **规则**：回调函数内**仅存储数据**，不进行计算。
- **方式**：使用 `Timer` 定时器以固定频率（如 50Hz）处理最新存储的数据。

```python
def imu_cb(self, msg):
    # 回调只做一件事：存起来！
    self.latest_imu = msg

def control_loop(self):
    # 在定时器回调中进行逻辑计算
    if self.latest_imu:
        ax = self.latest_imu.linear_acceleration.x
```

## 2. 图像数据处理：严禁直接订阅原始图
- **规则**：绝对不要订阅原始 `Image` 话题，尤其是通过 WiFi 连接时。
- **方式**：必须订阅 `.../compressed` 话题，并使用 `cv2` 解码。

```python
from sensor_msgs.msg import CompressedImage
import cv2

def image_cb(self, msg):
    # 解码压缩图
    np_arr = np.frombuffer(msg.data, np.uint8)
    cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
```

## 3. 点云数据解析：推荐使用工具库
- **规则**：不要手动解析 `PointCloud2` 的二进制字节。
- **方式**：使用 `sensor_msgs_py` 提供的 `point_cloud2` 转换工具。

```python
from sensor_msgs_py import point_cloud2

def lidar_cb(self, msg):
    # 转为 numpy 数组进行处理
    points = np.array(list(point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)))
```

## 4. QoS 匹配规则
订阅传感器数据时，QoS 配置必须与底层发布端匹配。
- **激光雷达/IMU**：通常需使用 `BEST_EFFORT` 且 `TRANSIENT_LOCAL`。
- **相机**：通常使用 `BEST_EFFORT`。
