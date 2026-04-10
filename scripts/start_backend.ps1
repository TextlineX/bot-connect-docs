param(
  [string]$ModelPath = "",          # 为空则不启本地 ASR，由 master 识别
  [string]$PythonBin = "python",
  [int]$Port = 8765,
  [string]$AsrMode = "master"       # master | local | off
)

$env:WS_PORT = $Port
$env:ASR_MODE = $AsrMode
if ($ModelPath) { $env:MODEL_PATH = $ModelPath }
if ($PythonBin) { $env:PYTHON_BIN = $PythonBin }

cd H:\Project\Bot\bot_connect\backend
Write-Host "[start_backend] ASR_MODE=$env:ASR_MODE MODEL_PATH=$($env:MODEL_PATH) PYTHON_BIN=$($env:PYTHON_BIN) WS_PORT=$env:WS_PORT"
node server.js
