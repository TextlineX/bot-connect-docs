# Simple PowerShell helper to run master/client.py in SIM_MODE (仅 WS，不依赖 ROS/TTS)
# 支持参数或环境变量：
#   ./scripts/start_master_sim.ps1 -WS_URL ws://192.168.31.170:8765 -ROBOT_ID master-01 -MasterModules all
#   （或事先 set WS_URL / set ROBOT_ID，再运行脚本）
# 默认 WS_URL=ws://127.0.0.1:8765，ROBOT_ID=master-01
# 需要已安装 Python，依赖从 requirements.txt 已装好。

param(
  [string]$WS_URL = "",
  [string]$ROBOT_ID = "",
  [string]$MasterModules = ""
)

$ErrorActionPreference = "Stop"

# 仓库根目录（容错：PSScriptRoot/PSCommandPath/MyInvocation 再退回当前目录）
$scriptDir = $PSScriptRoot
if (-not $scriptDir -and $PSCommandPath) { $scriptDir = Split-Path -Parent $PSCommandPath }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }
$root = Join-Path $scriptDir ".."
Set-Location $root

# 加载自定义配置（config/local.ps1），不存在则用默认
$cfg = Join-Path $root "config\local.ps1"
if ($cfg -and (Test-Path $cfg)) { . $cfg }

# 参数优先覆盖环境
if ($WS_URL) { $env:WS_URL = $WS_URL }
if ($ROBOT_ID) { $env:ROBOT_ID = $ROBOT_ID }
if ($MasterModules) { $env:MASTER_MODULES = $MasterModules }

# 一键默认配置（可按需改写/覆盖）
if (-not $env:WS_URL)   { $env:WS_URL   = "ws://127.0.0.1:8765" }
if (-not $env:ROBOT_ID) { $env:ROBOT_ID = "master-01" }
if (-not $env:MASTER_MODULES) { $env:MASTER_MODULES = "all" }

$env:SIM_MODE = "1"
$env:ROBOT_ROLE = "master"

Write-Host "[master-sim] WS_URL=$env:WS_URL ROBOT_ID=$env:ROBOT_ID SIM_MODE=1 MASTER_MODULES=$env:MASTER_MODULES"
try {
  python "$root\robot\client.py"
} catch {
  Write-Host "运行出错: $($_.Exception.Message)"
} finally {
  Write-Host "`n按 Enter 退出窗口..."
  Read-Host | Out-Null
}
