# 雷达点云解码优化指南

## 1. 问题描述
原始解码节点由于使用 Python `for` 循环解析二进制数据，导致帧率极低（约 0.4Hz），无法满足实时 SLAM 要求。

## 2. 性能攻坚：Numpy 向量化
- **目标**：将帧率提升至 10Hz 正常水平。
- **核心方案**：
  - 使用 `np.frombuffer` 批量解析雷达包数据。
  - 避免 Python 循环，使用内存切片替代。
  - 批量构造 `PointCloud2` 消息的 `data` 字段。

## 3. 点云字段格式规范 (FAST-LIO 兼容)
为了让 FAST-LIO 正确解析，点云字段必须严格按照以下顺序，且步长为 24 字节：

| 字段名 | 类型 | 偏移量 (Offset) |
| :--- | :--- | :--- |
| x | FLOAT32 | 0 |
| y | FLOAT32 | 4 |
| z | FLOAT32 | 8 |
| intensity | FLOAT32 | 12 |
| ring | FLOAT32 | 16 |
| time | FLOAT32 | 20 |

## 4. 优化脚本示例
```python
# 使用 numpy 的结构化数组快速填充
points = np.zeros(n_points, dtype=[
    ('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
    ('intensity', 'f4'), ('ring', 'f4'), ('time', 'f4')
])
points['x'] = xs
# ...
cloud.data = points.tobytes()
```

## 5. 解码避坑提示
- **XYZ 符号位**：C16 数据单维为 1 字节，转换时必须先转为 `int8` 再转为 `int16`。
- **距离过滤**：必须过滤掉 0.1m 以内的反射噪点。
