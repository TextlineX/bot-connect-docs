# 真机启动手册

## 快速启动

### 一键启动 PC 端

```powershell
cd H:\Project\Bot\bot_connect
.\scripts\start_relay.ps1 -ModelPath "H:\models\vosk-model-small-cn-0.22" -PythonBin "C:\Python314\python.exe"
```

### 一键启动全模拟

```powershell
.\scripts\start_full_stack.ps1 -MasterModules all -SimMode 1
```

效果：同时启动 `backend` + `frontend` + `master/client.py` 三个窗口。

## 配置同步

前端"设置"页保存后，会写入 `backend/config.json` 并通过 `config_sync` 下发到 Master / Slave。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 连接不上 | WS_URL 用错了 IP | 确认 PC 实际 IP |
| TTS 失败 | `/aimdk_5Fmsgs/srv/PlayTts` 不存在 | `ros2 service list \| grep PlayTts` 确认 |
| AI 未触发 | `ai.enabled` 未开启 | 前端设置里打开"主机 AI 解析" |
| 视频流无图 | `STREAM_PUBLIC_HOST` 错误 | 确认机器人实际 IP |
| ASR 无结果 | `MODEL_PATH` 未设置 | 设置 Vosk 模型路径 |
