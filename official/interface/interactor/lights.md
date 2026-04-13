<a id="id1"></a>

# 5.2.3 灯带控制

**胸前灯带控制接口提供了扩展的视觉交互功能。**

<a id="id2"></a>

## 核心特性

  * RGB分量独立控制

  * 多种显示模式支持

<a id="id3"></a>

## 灯带控制服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/LedStripCommand` | `LedStripCommand` | 灯带控制  
  
注意

灯带服务响应速度较慢, 应预期5秒左右时间完成调用。  
多任务时可放在单独线程中控制或异步调用。

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

  * `LedStripCommand` ros2-srv @ hal/srv/LedStripCommand.srv

```
# 灯带控制
# 服务名称: /aimdk_5Fmsgs/srv/LedStripCommand

# 请求
CommonRequest request  # 请求头

uint8 led_strip_mode  # 灯带模式(0:常亮, 1:呼吸, 2:闪烁, 3:流水)
uint8 r  # 红色分量0-255
uint8 g  # 绿色分量0-255
uint8 b  # 蓝色分量0-255

---

# 响应
ResponseHeader header  # 响应头
uint16 status_code  #状态码 (0:成功,其他-失败)
```

`led_strip_mode`说明:

值 | 模式 | 说明  
---|---|---  
0 | 常亮 |   
1 | 呼吸 | 4s周期, 亮度正弦变化  
2 | 闪烁 | 1s周期, 亮灭每0.5s切换  
3 | 流水 | 2s周期, 从左往右点亮，然后同时灭  

<a id="id4"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** ： [LED灯带控制](/official/examples/cpp/led)

  * **Python 示例** ： [LED灯带控制](/official/examples/python/led)
