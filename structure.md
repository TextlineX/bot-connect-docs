# 目录与保留文件清单
```
bot_connect/
├─ backend/          server.js, package.json
├─ frontend/         package.json, vite.config.js, index.html, src/**/*
├─ common/           ws_client.py, tts_client.py
├─ master/           client.py
├─ slave/            client.py
├─ docs/             pc.md, robot_master.md, robot_slave.md, structure.md
└─ README.md (可选)
```

# 排查速查
- 后端日志 `target ... offline`：主机/从机未连上后端。
- TTS 失败/超时：
  1) `ros2 service list | grep PlayTts` 是否有服务；
  2) `TTS_SERVICE` 是否匹配；
  3) 是否已 source ROS 环境。
- 前端连不上：确保 `node server.js` 在跑、防火墙放行 8765、WS_URL IP 正确。

# 清理建议
- 可删除：backend/frontend 内的 node_modules（随装随删）；临时脚本 send_cmd.py、根目录多余 tts_proxy.py 等。
- 删除前可备份：`robocopy H:\Project\Bot\bot_connect H:\Project\Bot\bot_connect_backup /MIR`
