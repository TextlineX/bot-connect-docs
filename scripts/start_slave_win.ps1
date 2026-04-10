# Windows 本地启动从机（默认本地模拟）
param(
  [Alias('WS_URL')][string]$WsUrl = "",
  [Alias('ROBOT_ID','SlaveId','SLAVE_ROBOT_ID')][string]$RobotId = "",
  [Alias('SIM_MODE')][string]$SimMode = "1"
)

$ErrorActionPreference = "Stop"

# 仓库根目录（容错：PSScriptRoot/PSCommandPath/MyInvocation/当前目录）
$scriptDir = $PSScriptRoot
if (-not $scriptDir -and $PSCommandPath) { $scriptDir = Split-Path -Parent $PSCommandPath }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }
$root = Join-Path $scriptDir ".."
Set-Location $root

# 加载自定义配置（如有）
$cfg = Join-Path $root "config\\local.ps1"
if ($cfg -and (Test-Path $cfg)) { . $cfg }

# 参数优先覆盖环境
if ($WsUrl) { $env:WS_URL = $WsUrl }
if ($RobotId) { $env:SLAVE_ROBOT_ID = $RobotId }
if ($SimMode) { $env:SIM_MODE = $SimMode }

# 默认值
if (-not $env:WS_URL) { $env:WS_URL = "ws://127.0.0.1:8765" }
if ($env:SLAVE_ROBOT_ID) { $env:ROBOT_ID = $env:SLAVE_ROBOT_ID }
elseif (-not $env:ROBOT_ID -or $env:ROBOT_ID -eq "master-01") { $env:ROBOT_ID = "slave-01" }
if (-not $env:SIM_MODE) { $env:SIM_MODE = "1" }
$env:ROBOT_ROLE = "slave"

Write-Host "[slave-win] WS_URL=$env:WS_URL ROBOT_ID=$env:ROBOT_ID SIM_MODE=$env:SIM_MODE"
try {
  python "$root\robot\client.py"
} catch {
  Write-Host "运行出错: $($_.Exception.Message)"
} finally {
  Write-Host "`n按 Enter 退出窗口..."
  Read-Host | Out-Null
}
