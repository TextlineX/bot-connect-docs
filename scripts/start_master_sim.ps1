# Simple PowerShell helper to run master/client.py in SIM_MODE (仅 WS，不依赖 ROS/TTS)
# 支持参数或环境变量：
#   ./scripts/start_master_sim.ps1 -WS_URL ws://192.168.31.170:8765 -ROBOT_ID master-01
#   （或事先 set WS_URL / set ROBOT_ID，再运行脚本）
# 默认 WS_URL=ws://127.0.0.1:8765，ROBOT_ID=master-01
# 需要已安装 Python，依赖从 requirements.txt 已装好。

$ErrorActionPreference = "Stop"

# 仓库根目录（纯 Windows PowerShell，避免 $PSScriptRoot 为空）
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent (Get-Location) }
$root = Join-Path $scriptDir ".."
Set-Location $root

# 加载自定义配置（config/local.ps1），不存在则用默认
$cfg = Join-Path $root "config\local.ps1"
if (Test-Path $cfg) { . $cfg }

# 一键默认配置（可按需改写/覆盖）
if (-not $env:WS_URL)   { $env:WS_URL   = "ws://127.0.0.1:8765" }
if (-not $env:ROBOT_ID) { $env:ROBOT_ID = "master-01" }

$env:SIM_MODE = "1"

Write-Host "[master-sim] WS_URL=$env:WS_URL ROBOT_ID=$env:ROBOT_ID SIM_MODE=1"
try {
  python "$root\master\client.py"
} catch {
  Write-Host "运行出错: $($_.Exception.Message)"
} finally {
  Write-Host "`n按 Enter 退出窗口..."
  Read-Host | Out-Null
}
