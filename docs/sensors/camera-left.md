# 📷 传感器详细档案：前右立体相机（实际存在）

> 现场测试确认：当前系统仅有 **前右** 立体相机话题，没有“左目”节点。保留此文件用于记录实际可用的右目流。

## 📡 基础通信参数
- **话题名称**: `/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed`
- **标定话题**: `/aima/hal/sensor/stereo_head_front_right/camera_info`
- **消息类型**: `sensor_msgs/msg/CompressedImage`（图像），`sensor_msgs/msg/CameraInfo`（标定）
- **QoS 观察**: 实测可直接订阅，未见 TRANSIENT_LOCAL；默认 VOLATILE/BEST_EFFORT 即可。

## 📊 运行特性
- **发布频率**: 实测 ≈10 Hz（图像）；camera_info 低频/按需发布，可能测不到 Hz。
- **数据格式**: JPEG 压缩流。

## ⚠️ 使用提示
1. camera_info 低频，订阅算法时请容忍首次等待；如需稳定频率，可在上游补齐。
2. 建议在机器人本机做解码与降采样，避免在远端直接 `echo` 造成带宽/CPU 压力。
3. 处理链示例：`CompressedImage` → `cv2.imdecode` → 按需求 `resize` 后再送入感知/识别。
