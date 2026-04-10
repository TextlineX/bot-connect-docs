# One-click launcher for backend + frontend + master client
param(
  [string]$ModelPath = "",
  [string]$PythonBin = "python",
  [int]$WsPort = 8765,
  [int]$DevPort = 5173,
  [string]$RobotId = "master-01",
  [string]$SlaveRobotId = "slave-01",
  [string]$MasterModules = "all",
  [string]$SimMode = "1",
  [switch]$StartSlave,
  [string]$AsrMode = "master"   # master | local | off
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { throw "Cannot resolve script directory." }

$relay = Join-Path $scriptDir "start_relay.ps1"
$master = Join-Path $scriptDir "start_master_win.ps1"
$slave = Join-Path $scriptDir "start_slave_win.ps1"

if (-not (Test-Path $relay)) { throw "Missing relay launcher: $relay" }
if (-not (Test-Path $master)) { throw "Missing master launcher: $master" }
if ($StartSlave -and -not (Test-Path $slave)) { throw "Missing slave launcher: $slave" }

$masterWsUrl = "ws://127.0.0.1:$WsPort"

$relayArgs = @(
  "-NoLogo",
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", $relay,
  "-ModelPath", $ModelPath,
  "-PythonBin", $PythonBin,
  "-WsPort", "$WsPort",
  "-DevPort", "$DevPort",
  "-AsrMode", "$AsrMode"
)
Start-Process powershell -ArgumentList $relayArgs

Start-Sleep -Seconds 2

$masterArgs = @(
  "-NoLogo",
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", $master,
  "-WsUrl", $masterWsUrl,
  "-RobotId", $RobotId,
  "-MasterModules", $MasterModules,
  "-SimMode", $SimMode
)
Start-Process powershell -ArgumentList $masterArgs

if ($StartSlave) {
  $slaveArgs = @(
    "-NoLogo",
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $slave,
    "-WsUrl", $masterWsUrl,
    "-RobotId", $SlaveRobotId,
    "-SimMode", $SimMode
  )
  Start-Process powershell -ArgumentList $slaveArgs
}

Write-Host "Full stack launcher finished."
Write-Host "Backend: ws://127.0.0.1:$WsPort"
Write-Host "Frontend: http://127.0.0.1:$DevPort"
Write-Host "Master: robot_id=$RobotId MASTER_MODULES=$MasterModules SIM_MODE=$SimMode"
if ($StartSlave) {
  Write-Host "Slave: robot_id=$SlaveRobotId SIM_MODE=$SimMode"
}
Write-Host "ASR_MODE=$AsrMode MODEL_PATH=$ModelPath"
