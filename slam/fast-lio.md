# FAST-LIO 算法对接指南

## 1. 算法选型：FAST-LIO2
- **核心突破**：
  - **直接点云配准**：利用原始点云与地图匹配，不提取特征。
  - **增量 ikd-Tree**：支持点云地图的高效增量更新。
- **优点**：计算效率高，适合 X2 Ultra 实时建图。

## 2. 系统对接流程

### 阶段一：点亮 FAST-LIO (当前阶段)
让算法成功接收点云和 IMU 数据。
- **Launch 修改**：配置正确的话题名。
  - 点云：`/aima/hal/sensor/lidar_chest_front/decoded_pointcloud`
  - IMU：`/aima/hal/sensor/lidar_chest_front/imu`
- **外参 TF 确认**：配置 `lidar_imu_chest_front` 坐标系。

### 阶段二：坐标系与 TF 对齐
确保建图不倾斜、不飘移。
- 确认机器人是否发布了 `base_link -> lidar_chest_front` 的 TF。
- 否则需使用 `static_transform_publisher` 发布静态外参。

### 阶段三：实战建图与保存
- **推车测试**：缓慢移动机器人，观察 Rviz 中的点云重叠。
- **保存地图**：通过 `std_srvs/srv/Trigger` 触发 `save_map` 服务。

## 3. 常见问题排错
- **Points num 为 0**：检查话题名是否拼错或 QoS 是否匹配。
- **Fixed Frame 选错**：Rviz 必须将 Fixed Frame 设置为 `camera_init`。
- **地图漂移**：外参估计配置错误，应关闭 `extrinsic_est_en`。
