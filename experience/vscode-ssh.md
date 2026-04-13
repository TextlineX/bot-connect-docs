# VSCode SSH 连接

通过 VSCode 的 Remote-SSH 插件直接在机器人开发计算单元上编写和运行代码。

## 安装插件

在 VSCode 扩展市场搜索 **Remote - SSH**，安装 Microsoft 出品的官方插件。

## 配置 SSH 连接

### 1. 添加 SSH 连接配置

打开命令面板（`Ctrl+Shift+P`），输入并选择 **Remote-SSH: Open Configuration File**，选择 `~/.ssh/config`（Windows 上为 `C:\Users\<用户名>\.ssh\config`）。

添加以下内容：

```
Host x2-robot
    HostName 10.0.1.41
    User agi
    Port 22
```

> 有线直连时使用 `10.0.1.41`，AP 热点模式下使用 `192.168.88.88`。

### 2. 连接

在 VSCode 左侧 **Remote Explorer** 面板中，找到 `x2-robot`，右键点击 **Connect in New Window**，输入密码即可。

## 建议配置

### 同步设置

安装 **Settings Sync** 插件（或登录 GitHub 账号），将本地 VSCode 设置同步到远程，保持编辑体验一致。

### 打开远程目录

连接后，按 `Ctrl+K Ctrl+O` 打开远程工作目录，推荐：

- 开发计算单元：`/agibot/data/home/agi/`
- SDK 目录：`/agibot/data/home/agi/aimdk/`

### 终端编码

SSH 连接后，VSCode 终端默认编码通常为 UTF-8。如遇中文乱码，可在 VSCode 设置中添加：

```json
"terminal.integrated.env.linux": { "LC_ALL": "zh_CN.UTF-8" }
```

## 常用快捷键

| 功能 | 快捷键 |
|------|--------|
| 打开命令面板 | `Ctrl+Shift+P` |
| 打开远程目录 | `Ctrl+K Ctrl+O` |
| 新建终端 | `Ctrl+Shift+\`` |
| 文件搜索 | `Ctrl+Shift+F` |
