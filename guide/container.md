# 容器环境修复

## 常见问题

### WSL 下 .sh 脚本执行失败

```bash
# 提示 #!/usr/bin/env: No such file
dos2unix scripts/*.sh
chmod +x scripts/*.sh
```

### 路径问题

WSL 下项目路径：`/mnt/h/Project/Bot/bot_connect`

Windows 下项目路径：`H:\Project\Bot\bot_connect`

两者可混用，WSL 自动挂载 Windows 盘符。
