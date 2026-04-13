<a id="mc"></a>

# 5.1.3 MC控制信号设置

**MC控制信号设置实现了多输入源统一管理，确保机器人始终响应优先级最高的控制信号。**

控制信号设置是智元机器人X2 AimDK的核心功能之一，支持多个控制源的统一管理和优先级仲裁。该功能确保机器人在面对多个控制源时能够安全、可靠地响应最高优先级的控制指令。

<a id="id1"></a>

## 核心特性

<a id="mc-input-source-list"></a>

### 多源接入

  * **RC控制** : PS5遥控手柄控制（优先级80）

  * **VR控制** : 遥操控制（优先级70）

  * **APP控制** : 移动应用控制（优先级60）

  * **语音控制** : 语音指令控制（优先级50）

  * …

  * **二次开发** : 自定义控制源（优先级20-100可配置）

<a id="id2"></a>

### 优先级管理

  * **动态调整** ：支持运行时动态调整优先级

  * **自动仲裁** ：自动选择最高优先级输入源

  * **冲突处理** ：同优先级时响应最先接入的源

<a id="id3"></a>

## 输入源配置

<a id="id4"></a>

### 优先级参考

  * **100-80** ：系统级控制（紧急停止、安全模式）

  * **79-60** ：高级控制（遥控器、APP）

  * **59-40** ：中级控制（语音、手势）

  * **39-20** ：低级控制（二次开发）

  * **19-0** ：备用控制（调试、测试）

<a id="id5"></a>

## 仲裁流程

<a id="id6"></a>

### 仲裁机制

**输入源仲裁和管理规则：**

  * 被禁用的输入源和未知输入源, 其控制指令被丢弃

  * 从未被丢弃指令的输入源中选定最高优先级的有效输入源，只接受其控制

  * 出现非选定的更高优先级有效输入源时，改选其作为选定输入源

  * 选定输入源非活跃状态(timeout等)则被视为最低优先级, 将从活跃的其他有效控制源中重新选定

**注意系统重启后输入源优先级状态将重置**

二次开发的模块应结合以上情况, 注册**其他名称** 的控制源并设置优先级 (建议20-100)

系统内的既有控制输入源情况如下:

`source` | 说明 | 优先级 | 超时阀值(ms)  
---|---|---|---  
rc | 遥控手柄 | 80 | 1000  
app_proxy | 移动APP端Agibot Go | 60 | 1000  
vr | 遥操模块 | 70 | 1000  
interaction | 智元灵犀交互模块 | 50 | 1000  
pnc | 智元灵犀Planner模块 | 40 | 1000  
  
<a id="id7"></a>

## 输入源管理服务

服务名称 | 数据类型 | 描述  
---|---|---  
`/aimdk_5Fmsgs/srv/GetCurrentInputSource` | `GetCurrentInputSource` | 查询当前控制输入源  
`/aimdk_5Fmsgs/srv/SetMcInputSource` | `SetMcInputSource` | 设置输入源  
  
  * `GetCurrentInputSource` ros2-srv @ mc/motion/srv/GetCurrentInputSource.srv

```
# 获取当前控制输入源
# 服务名称: /aimdk_5Fmsgs/srv/GetCurrentInputSource

# 请求
CommonRequest request        # 公共请求头

---

# 响应
CommonTaskResponse response  # 公共任务响应, response.header.code为0表成功
McInputSource input_source  # 输入源
```

    * `McInputSource` ros2-msg @ mc/motion/McInputSource.msg

```
string name               # 当前选定的输入源名称, 如rc/vr/app_proxy/...
int32 priority              # 配置状态:优先级(0-100)
int32 timeout               # 配置状态:超时时间(ms)
```

  * `SetMcInputSource` ros2-srv @ mc/motion/srv/SetMcInputSource.srv

```
# 服务名称: /aimdk_5Fmsgs/srv/SetMcInputSource

# 请求
CommonRequest request        # 公共请求头
McInputAction action         # 操作类型 (ADD/MODIFY/DELETE/DISABLE/ENABLE)
McInputSource input_source   # 输入源

---

# 响应

CommonTaskResponse response  # response.header.code 0表成功
```

    * `McInputAction` ros2-msg @ mc/motion/McInputAction.msg

```
int32 value  # 操作类型 (1001:ADD, 1002:MODIFY, 1003:DELETE, 2001:ENABLE, 2002:DISABLE)
```

操作类型(值) | 说明 | `input_source`必须参数  
---|---|---  
ADD(1001) | 添加新输入源 | `name`, `priority`, `timeout`  
MODIFY(1002) | 修改现有输入源 | `name`, `priority`, `timeout`  
DELETE(1003) | 删除输入源 | `name`  
ENABLE(2001) | 启用输入源 | `name`  
DISABLE(2002) | 禁用输入源 | `name`  

<a id="id8"></a>

## 编程示例

详细的编程示例和代码说明请参考：

  * **C++ 示例** :

    * [注册二开输入源](/official/examples/cpp/input-register)

    * [获取当前输入源](/official/examples/cpp/input-get)

  * **Python 示例** :

    * [注册二开输入源](/official/examples/python/input-register)

    * [获取当前输入源](/official/examples/python/input-get)

<a id="id9"></a>

## 注意事项

重要

**版本兼容性** MC控制信号设置功能仅在X2_AimDK-v0.7及之后的版本中可用，不支持0.6及之前的版本。

注意

二次开发的模块应结合系统模块情况, 注册**其他名称** 的控制源并设置优先级 (建议20-100)

小心

ROS的服务(service)机制在跨板通信时存在一些待优化问题, **二次开发时请参考例程添加异常处理、快速重试等保护机制**

备注

运控系统未获取任意有效输入前(如刚上电启动未操作移动, 下发速度控制量全为0), 查询当前输入源可能为空
