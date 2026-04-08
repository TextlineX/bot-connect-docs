param(
  [string]$ModelPath = "H:\\models\\vosk-model-small-cn-0.22",
  [string]$PythonBin = "C:\\Python314\\python.exe",
  [int]$Port = 8765
)

$env:MODEL_PATH = $ModelPath
$env:PYTHON_BIN = $PythonBin
$env:WS_PORT = $Port
cd H:\Project\Bot\bot_connect\backend
Write-Host "[start_backend] MODEL_PATH=$env:MODEL_PATH PYTHON_BIN=$env:PYTHON_BIN WS_PORT=$env:WS_PORT"
node server.js
