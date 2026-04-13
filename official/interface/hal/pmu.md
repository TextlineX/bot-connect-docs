<a id="pmu"></a>

# 5.4.2 电源管理单元 (PMU)

**电源管理单元接口提供了机器人电源系统的监控和管理能力，包括电池状态、电压电流监控等功能。**

<a id="id1"></a>

## 核心功能

<a id="id2"></a>

### 电池监控

  * **电池电压** ：实时监控电池电压状态

  * **电池电流** ：监控电池充放电电流

  * **电池状态** ：电池健康状态监控

<a id="id3"></a>

### 电源管理

  * **多路电源** ：48V、12V、5V等多路电源监控

  * **电流监控** ：各模块电流消耗监控

  * **电压监控** ：各模块电压状态监控

<a id="id4"></a>

### 系统监控

  * **电源模块状态** ：RK3588、ORIN等模块电源状态

  * **过流保护** ：过流检测和保护

<a id="id5"></a>

## 电源管理话题

话题名称 | 数据类型 | 描述 | QoS | 频率  
---|---|---|---|---  
`/aima/hal/pmu/state` | `PmuState` | 电源管理数据 | - | 0.2Hz  
  
  * `PmuState` ros2-msg @ hal/msg/PmuState.msg

```
# 电源管理单元状态
string pmu_software_version     # PMU软件版本
string pmu_hardware_version     # PMU硬件版本
string pmu_protocol_version     # PMU协议版本
uint32 pmu_bool_status          # 布尔状态位

# 电流信息 (单位: A)
float64 head_power_current      # 头部电流
float64 output_48v_current      # 48V输出电流
float64 rk3588_current          # RK3588电流
float64 output_12v_current      # 12V输出电流
float64 bus_48v_current         # 48V总线电流
float64 orin_current            # ORIN电流

# 电压信息 (单位: V)
float64 bus_48v_pmos_voltage    # 48V PMOS电压
float64 battery_voltage         # 电池电压
float64 fan_voltage             # 风扇电压
float64 output_12v_voltage      # 12V输出电压
float64 output_48v_voltage      # 48V输出电压
float64 bus_48v_voltage         # 48V总线电压
float64 head_power_voltage      # 头部电压
float64 orin_voltage            # ORIN电压
float64 rk3588_voltage          # RK3588电压

# BMS信息
string bms_manufacturer         # BMS厂家信息
string bms_serial_number        # BMS序列号
string bms_hardware_version                 # 硬件版本
string bms_software_version                 # 软件版本

uint32 bms_status_bits                      # 状态位和状态码

uint16 battery_balance_line_resistance      # 电池包均衡线电阻（单位：mΩ）
float64 battery_pack_voltage                # 电池包电压（单位：V）
float64 battery_current                     # 电池包电流（单位：A，充电为正，放电为负）
float64 battery_output_power                # 电池包输出功率（单位：W）
float64 battery_temperature                 # 电池包当前温度（单位：℃）
uint32 battery_remaining_capacity           # 当前电池剩余容量（单位：mAh）
uint8 battery_remaining_capacity_percentage # 当前电池剩余容量百分比（单位：%）
uint16 battery_cycle_count                  # 当前电池包完整循环次数（单位：次）
uint32 battery_cycle_total_capacity         # 总充放电容量累计（单位：Ah）
```

`pmu_bool_status`布尔位状态说明:

位 | 名称 | 描述  
---|---|---  
0 | rk3588PowerGood | RK3588 电源状态  
1 | rk3588Monitor1 | RK3588 监控状态1  
2 | rk3588Monitor2 | RK3588 监控状态2  
3 | orinPowerGood | ORIN 电源状态  
4 | orinMonitor1 | ORIN 监控状态1  
5 | orinMonitor2 | ORIN 监控状态2  
6 | bus48vOverCurrent | 48V 总线过流  
7 | bus48vOverTemperature | 48V 总线过温  
8 | rk3588PlugDetect | RK3588 插入检测  
9 | orinNXPlugDetect | ORIN NX 插入检测  
10-31 | reserved | 保留位  
  
`bms_status_bits`状态位说明:

位 | 名称 | 描述  
---|---|---  
0 | chargeFlag | 充电标志  
1 | chargeOverCurrentFlag | 充电过流标志  
2 | dischargeFlag | 放电标志  
3 | dischargeOverCurrentFlag | 放电过流标志  
4 | shortCircuitFlag | 电池短路标志  
5 | cellOverVoltageFlag | 电芯电压过压标志  
6 | cellUnderVoltageFlag | 电芯电压欠压标志  
7 | batteryOverVoltageFlag | 电池总电压过压标志  
8 | batteryUnderVoltageFlag | 电池总电压欠压标志  
9 | cellOpenCircuitFlag | 电芯检测到开路标志  
10 | ntcOpenCircuitFlag | 温度传感器检测到开路标志  
11 | cellDischargeOverTemperatureFlag | 电芯温度超过放电温度上限标志  
12 | cellChargeOverTemperatureFlag | 电芯温度超过充电温度上限标志  
13 | cellDischargeUnderTemperatureFlag | 电芯温度低于放电温度下限标志  
14 | cellChargeUnderTemperatureFlag | 电芯温度低于充电温度下限标志  
15 | reserved_1 | 保留位  
16 | cellMaxVoltageDiffOverHighFlag | 电芯最大电压差超过上限标志  
17 | mosfetChargeDisableFlag | MOSFET禁止充电标志  
18 | mosfetDischargeDisableFlag | MOSFET禁止放电标志  
19 | mosfetOverTemperatureFlag | MOSFET温度超过工作温度上限标志  
20 | balanceLineResistanceOverHighFlag | 电池包均衡线电阻超过上限标志  
21~31 | reserved_11 | 保留位  

<a id="id6"></a>

## 安全注意事项

警告

**电源管理限制**

  * 电源管理涉及系统安全，请谨慎操作

  * 不要随意修改电源参数，可能导致系统损坏

  * 建议在专业人员指导下进行电源相关操作

备注

**最佳实践**

  * 定期监控电源状态，及时发现异常

  * 实现电源状态监控和告警机制

  * 建议实现电源保护策略

  * 注意电源模块的温度和电流限制
