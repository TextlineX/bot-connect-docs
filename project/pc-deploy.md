# PC 端部署

## 后端 (Node.js)

```powershell
cd H:\Project\Bot\bot_connect\backend
npm install
node server.js
```

默认监听 `ws://0.0.0.0:8765`。

**环境变量：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WS_HOST` | `0.0.0.0` | 监听地址 |
| `WS_PORT` | `8765` | 监听端口 |
| `AUTH_TOKEN` | — | 开启鉴权 |
| `MODEL_PATH` | — | Vosk 模型路径，开启本地 ASR |
| `PYTHON_BIN` | `python` | Python 解释器路径 |
| `FFMPEG_BIN` | `ffmpeg` | ffmpeg 路径 |

## 前端 (Vue + Vite)

```powershell
cd H:\Project\Bot\bot_connect\frontend
npm install
npm run dev -- --host --port 5173
```

浏览器访问 `http://<PC_IP>:5173`。

## 一键启动

```powershell
cd H:\Project\Bot\bot_connect
.\scripts\start_relay.ps1 -ModelPath "H:\models\vosk-model-small-cn-0.22" -PythonBin "C:\Python314\python.exe" -WsPort 8765 -DevPort 5173
```

## Electron 客户端（可选）

解决浏览器 HTTP 环境下的音频 API 限制：

```powershell
cd H:\Project\Bot\bot_connect\frontend
npm install
npm run electron:dev
```

- `electron:dev` — 开发模式
- `electron:build` — 构建 + 运行
- `electron:preview` — 预览已构建产物

## 防火墙

确保 Windows 防火墙放行 **8765** 端口。

## 全模拟模式（无 ROS）

```powershell
# 后端 + 前端
.\scripts\start_relay.ps1 ...

# 主机模拟
$env:WS_URL="ws://<PC_IP>:8765"
$env:ROBOT_ID="master-01"
$env:SIM_MODE="1"
python H:\Project\Bot\bot_connect\master\client.py

# 从机模拟
$env:WS_URL="ws://<PC_IP>:8765"
$env:ROBOT_ID="slave-01"
python H:\Project\Bot\bot_connect\slave\client.py
```
