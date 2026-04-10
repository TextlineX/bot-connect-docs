# 动作回归与映射说明

## 目的
- 统一「官方预设动作」与前端按钮的映射，区分左右部位。
- 提供独立测试脚本，便于在本地或真机逐条验证动作链路（controller → backend → master/slave → result）。

## 测试脚本：`scripts/test_actions.py`
- 依赖：`pip install websockets`
- 基本用法（本地模拟）：
  ```powershell
  cd H:\Project\Bot\bot_connect
  python scripts\test_actions.py ws://127.0.0.1:8765 --target master-01 --side right --delay 2
  ```
- 常用参数：
  - `ws_url`：后端 WS 地址，例如 `ws://<PC_IP>:8765`。
  - `--target`：动作下发目标，默认 `master-01`（若要直接测从机可改成 `slave-01`）。
  - `--side`：`left | right | both`，仅测试对应侧的动作。
  - `--only`：只测指定动作，逗号分隔，如 `--only wave_left,salute_left`。
  - `--delay`：两条动作之间的间隔秒数，默认 1.5。
- 行为：脚本先发送 `hello`，随后按列表逐条发 `exec/preset.run` 帧，并打印收到的 `result/status/ai_result`，用于确认链路和回执。

## 官方动作映射（已对齐前端按钮 & 测试脚本）

| 按钮/名称 | action | motion_id | area_id | 侧别 |
| --- | --- | --- | --- | --- |
| 挥手(右) | preset.run / wave | 1002 | 2 | 右 |
| 挥手(左) | preset.run / wave_left | 1002 | 1 | 左 |
| 握手(右) | preset.run / handshake | 1003 | 2 | 右 |
| 握手(左) | preset.run / handshake_left | 1003 | 1 | 左 |
| 举手(右) | preset.run / raise_hand | 1001 | 2 | 右 |
| 举手(左) | preset.run / raise_hand_left | 1001 | 1 | 左 |
| 飞吻(右) | preset.run / kiss | 1004 | 2 | 右 |
| 飞吻(左) | preset.run / kiss_left | 1004 | 1 | 左 |
| 敬礼(右) | preset.run / salute | 1013 | 2 | 右 |
| 敬礼(左) | preset.run / salute_left | 1013 | 1 | 左 |
| 鼓掌 | preset.run / clap | 3017 | 11 | 双 |
| 加油 | preset.run / cheer | 3011 | 11 | 双 |
| 鞠躬 | preset.run / bow | 3001 | 11 | 双 |
| 跳舞 | preset.run / dance | 3007 | 11 | 双 |

## 前端映射位置
- 控制页：`frontend/src/views/ControlView.vue`  
  - “基础移动”：前进/后退/左转/右转/停止 → `cmd_vel` 或 `motion.stop`。  
  - “官方预设”：上表所有动作按按钮直发 `exec`，payload 含 `action=name/motion_id/area_id`，默认发送到 “控制目标” 机器人（设置页可改）。

## 测试建议
1) 按启动顺序：backend → frontend → master（SIM_MODE=1 可用仿真）→ slave。前端设置脑=master-01、控制=slave-01 后“保存并同步”。  
2) 先用前端按钮观察 master/slave 终端是否出现对应动作/回执。  
3) 再用 `scripts/test_actions.py` 跑一轮回归，确认所有预设返回 `ok=true`。  
4) 真机时把 `--target` 指向真实 ID，必要时关闭 SIM_MODE。正在调试的新动作可先加到脚本/表格，确认通过后再挂到前端按钮。  

## 扩展新动作
- 在 master 的 `master/handlers/action_router.py` 补充 PRESET_DEFS / ALIASES。
- 将同名映射追加到：
  - 测试脚本 `PRESET_DEFS`
  - 前端 `presetActions` 列表（ControlView.vue）
- 真机测试通过后再提供给 AI / 上层逻辑调用。 
