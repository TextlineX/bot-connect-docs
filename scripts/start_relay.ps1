# 一键启动后端+前端（各自独立窗口）
param(
  [string]$ModelPath = "",
  [string]$PythonBin = "python",
  [int]$WsPort = 8765,
  [int]$DevPort = 5173,
  [string]$AsrMode = "master"    # master | local | off
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { throw "无法确定脚本目录" }

$backend = Join-Path $scriptDir "start_backend.ps1"
$frontend = Join-Path $scriptDir "start_frontend.ps1"

if (-not (Test-Path $backend)) { throw "未找到后端启动脚本: $backend" }
if (-not (Test-Path $frontend)) { throw "未找到前端启动脚本: $frontend" }

Start-Process powershell -ArgumentList "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$backend`" -ModelPath `"$ModelPath`" -PythonBin `"$PythonBin`" -Port $WsPort -AsrMode $AsrMode"
Start-Process powershell -ArgumentList "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$frontend`" -Port $DevPort"

Write-Host "Relay launcher finished."
Write-Host "Backend window: ws://0.0.0.0:$WsPort"
Write-Host "Frontend window: http://<PC_IP>:$DevPort"
