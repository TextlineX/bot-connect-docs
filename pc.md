# PC 侧部署与运行

## 后端 (Node)
位置：backend/
```
cd H:\Project\Bot\bot_connect\backend
npm install
node server.js   # ws://0.0.0.0:8765
```
可选环境：WS_HOST / WS_PORT / AUTH_TOKEN

## 前端 (Vue + Vite)
位置：frontend/
```
cd H:\Project\Bot\bot_connect\frontend
npm install
npm run dev -- --host --port 5173
```
浏览器：`http://<PC_IP>:5173`，WS 地址填 `ws://<PC_IP>:8765`。
功能：发送 cmd_vel，发送 TTS（action=tts），查看 result 回调。

## 注意
- Windows 防火墙放行 8765。
- node_modules 可随删随装，不需同步到机器人。
