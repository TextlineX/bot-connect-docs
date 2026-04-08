后端改为 Node.js 版本已就位：
- 位置：H:\Project\Bot\bot_connect\backend
  - server.js  (基于 ws)
  - package.json (依赖 ws + dotenv)

运行后端
1) cd H:\Project\Bot\bot_connect\backend
2) npm install
3) npm start   # 默认监听 ws://0.0.0.0:8765
可选环境变量：WS_HOST、WS_PORT、AUTH_TOKEN（开启鉴权）。

主/从客户端文件保持不变（Python），指向同一个 WS_URL 即可直接互通。

下一步可测试：
- 启动 server.js
- 启动 master/slave Python 客户端
- 用之前的控制脚本发送 cmd_vel，观察打印即可确认链路。
