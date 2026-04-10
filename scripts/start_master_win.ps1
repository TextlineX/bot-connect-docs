# Windows 一键启动主机客户端（可选 ROS/TTS，默认 SIM_MODE=1）
# 读取 config\local.ps1 中的 WS_URL / ROBOT_ID / TTS_SERVICE / MASTER_MODULES 等环境

param(
  [string]$WsUrl = "",
  [string]$RobotId = "",
  [string]$TtsService = "",
  [string]$MasterModules = "",
  [string]$SimMode = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Split-Path -Parent $root
Set-Location $root

# 加载自定义配置
$cfg = Join-Path $root "config\\local.ps1"
if ($cfg -and (Test-Path $cfg)) { . $cfg }

# 参数优先覆盖环境
if ($WsUrl) { $env:WS_URL = $WsUrl }
if ($RobotId) { $env:MASTER_ROBOT_ID = $RobotId }
if ($TtsService) { $env:TTS_SERVICE = $TtsService }
if ($MasterModules) { $env:MASTER_MODULES = $MasterModules }
if ($SimMode) { $env:SIM_MODE = $SimMode }

# 清理隐藏空格/不可见字符，避免看似“空”的值导致不走默认
$env:WS_URL = ([string]$env:WS_URL).Trim()
$env:ROBOT_ID = ([string]$env:ROBOT_ID).Trim()
$env:MASTER_ROBOT_ID = ([string]$env:MASTER_ROBOT_ID).Trim()
$env:TTS_SERVICE = ([string]$env:TTS_SERVICE).Trim()
$env:MASTER_MODULES = ([string]$env:MASTER_MODULES).Trim()
$env:SIM_MODE = ([string]$env:SIM_MODE).Trim()

# 默认值
if (-not $env:WS_URL)   { $env:WS_URL   = "ws://192.168.31.170:8765" }
if ($env:MASTER_ROBOT_ID) { $env:ROBOT_ID = $env:MASTER_ROBOT_ID }
elseif (-not $env:ROBOT_ID) { $env:ROBOT_ID = "master-01" }
if (-not $env:TTS_SERVICE) { $env:TTS_SERVICE = "/aimdk_5Fmsgs/srv/PlayTts" }
if (-not $env:MASTER_MODULES) { $env:MASTER_MODULES = "all" }
$env:ROBOT_ROLE = "master"

# 是否强制模拟（无 ROS/TTS）
if (-not $env:SIM_MODE) { $env:SIM_MODE = "1" }  # 默认只走 WS

Write-Host "[master-win] WS_URL='$env:WS_URL' ROBOT_ID='$env:ROBOT_ID' SIM_MODE='$env:SIM_MODE' TTS_SERVICE='$env:TTS_SERVICE' MASTER_MODULES='$env:MASTER_MODULES'"
try {
  python "$root\robot\client.py"
} catch {
  Write-Host "运行出错: $($_.Exception.Message)"
} finally {
  Write-Host "`n按 Enter 退出窗口..."
  Read-Host | Out-Null
}
