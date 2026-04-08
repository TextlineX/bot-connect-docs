# 一键启动后端+前端（各自独立窗口）
param(
  [string]$ModelPath = "H:\\models\\vosk-model-small-cn-0.22",
  [string]$PythonBin = "C:\\Python314\\python.exe",
  [int]$WsPort = 8765,
  [int]$DevPort = 5173
)

$root = "H:\Project\Bot\bot_connect\scripts"
$backend = Join-Path $root "start_backend.ps1"
$frontend = Join-Path $root "start_frontend.ps1"

Start-Process powershell -ArgumentList "-NoLogo -ExecutionPolicy Bypass -File `"$backend`" -ModelPath `"$ModelPath`" -PythonBin `"$PythonBin`" -Port $WsPort"
Start-Process powershell -ArgumentList "-NoLogo -ExecutionPolicy Bypass -File `"$frontend`" -Port $DevPort"

Write-Host "Relay started: backend ws://0.0.0.0:$WsPort , frontend http://<PC_IP>:$DevPort"
