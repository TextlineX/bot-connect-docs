<a id="id1"></a>

# 8 __特殊过渡方案声明

  * 在SDK迭代过程中，我们提供一些**临时手段和临时说明** 来支持一些高级的二开需求、声明一些暂未开放但即将开放的接口属性、根据系统架构调整废弃一些接口/参数.

  * 在SDK的后续迭代中，这些过渡方案会被更加自洽、更加全面的软硬件环境闭环掉，敬请期待…

<a id="agent-only-voice"></a>

## 8.1 关闭 X2 自带的交互能力，开发您自己的语音系统

**默认情况下，机器人上电后会自动进入自然语音交互模式，交互模块会占用音频输入输出流。** 如需集成自研语音系统并获取音频流，可通过以下步骤临时关闭机器人自带的交互功能，将音频流释放给您的系统。**后续版本将支持一键切换交互二开模式，进一步简化自研语音系统的开发流程。**

<a id="id2"></a>

### 8.1.1 临时关闭内置交互系统操作步骤

  1. 机器人上电。

  2. 切换交互模式（禁用大模型），执行以下命令：

```bash
ros2 service call /aimdk_5Fmsgs/srv/SetAgentPropertiesRequest aimdk_msgs/srv/SetAgentPropertiesRequest "
contents:
  properties:
    - key:
        value: 2  # AGENT_PROPERTY_RUN_MODE = 0x02
      value: 'only_voice'
"
```

> 该操作会在本地文件中设置模式，禁用大模型。

  3. 重启 agent 模块以使设置生效：

```bash
# 关闭交互模块
aima em stop-app agent

# 以二开模式启动交互模块
aima em start-app agent
```

  4. 订阅音频数据并进行二次开发。具体方法可参考[MIC音频流采集话题](/official/interface/interactor/voice#mic-receiver-vad)章节。

* * *

<a id="id3"></a>

### 8.1.2 恢复内置交互系统操作步骤

  1. 机器人上电。

  2. 切换回正常交互模式，执行以下命令：

```bash
ros2 service call /aimdk_5Fmsgs/srv/SetAgentPropertiesRequest aimdk_msgs/srv/SetAgentPropertiesRequest "
contents:
  properties:
    - key:
        value: 2  # AGENT_PROPERTY_RUN_MODE = 0x02
      value: 'normal'
"
```

  3. 重启 agent 模块：

```bash
aima em stop-app agent

# 以正常模式启动交互模块
aima em start-app agent
```

  4. 此时可正常使用智元大模型进行交互。

<a id="v0-7-xmcaction"></a>

## 8.2 机器人运动状态精简，v0.7.x及之前的部分McAction状态码不再支持

小心

**v0.8开始以下运动模式码请勿使用** 。这些状态码部分可能仍暂时存在，但效果无法保证，已不对二开开放。

  * `ZERO_TORQUE_DEFAULT`: 关联中文名`零力矩模式`仍沿用, 变更对应到`PASSIVE_DEFAULT`

  * `SOFT_EMERGENCY_STOP`: 软急停不再作为运动模式, 使用零力矩模式(`PASSIVE_DEFAULT`)和阻尼模式(`DAMPING_DEFAULT`)

  * `JOINT_FREEZE`: 取消, 使用站姿预备（位控站立）(`JOINT_DEFAULT`)对应关节完全锁定, 阻尼模式(`DAMPING_DEFAULT`)对应关节阻滞

  * `STAND_BODY_CONTROL`: 取消, 使用稳定站立(`STAND_DEFAULT`)

  * `RUN_DEFAULT`: 跑步运动取消, 使用走跑模式(`LOCOMOTION_DEFAULT`)
