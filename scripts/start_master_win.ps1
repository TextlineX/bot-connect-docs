# Windows 一键启动主机客户端（可选 ROS/TTS，默认 SIM_MODE=1）
# 读取 config\local.ps1 中的 WS_URL / ROBOT_ID / TTS_SERVICE 等环境

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Split-Path -Parent $root
Set-Location $root

# 加载自定义配置
$cfg = Join-Path $root "config\\local.ps1"
if ($cfg -and (Test-Path $cfg)) { . $cfg }

# 默认值
if (-not $env:WS_URL)   { $env:WS_URL   = "ws://192.168.31.170:8765" }
if (-not $env:ROBOT_ID) { $env:ROBOT_ID = "master-01" }
if (-not $env:TTS_SERVICE) { $env:TTS_SERVICE = "/aimdk_5Fmsgs/srv/PlayTts" }

# 是否强制模拟（无 ROS/TTS）
if (-not $env:SIM_MODE) { $env:SIM_MODE = "1" }  # 默认只走 WS

Write-Host "[master-win] WS_URL=$env:WS_URL ROBOT_ID=$env:ROBOT_ID SIM_MODE=$env:SIM_MODE TTS_SERVICE=$env:TTS_SERVICE"
try {
  python "$root\master\client.py"
} catch {
  Write-Host "运行出错: $($_.Exception.Message)"
} finally {
  Write-Host "`n按 Enter 退出窗口..."
  Read-Host | Out-Null
}
