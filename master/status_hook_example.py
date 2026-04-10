"""
可选的主机状态扩展示例：设置环境变量 MASTER_STATUS_HOOK=master.status_hook_example
后，master/client.py 会调用 get_status(sdk) 并把返回值 merge 进基础状态。

在真机环境，可以在这里读取 ROS 话题或系统信息，保持键名与 Dashboard
期望的结构一致（system / sensors / motion / audio 等）。
"""


def get_status(_sdk):
    # TODO: 在这里填充真实状态，例如从 ROS2 订阅:
    #  - 电池: /battery_state
    #  - IMU: /imu/data
    #  - Lidar 最近障碍: /scan
    #  - 机器姿态/模式: 自定义话题或服务
    return {
        "sensors": {
            # 例：将真实话题值写入这些字段
            # "battery_pct": battery_pct,
            # "imu_yaw_deg": yaw_deg,
            # "lidar_distance_m": nearest_obs_m,
        }
    }
