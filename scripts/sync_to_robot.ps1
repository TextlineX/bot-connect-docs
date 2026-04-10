# Windows/PowerShell 同步到机器人（依赖 rsync）
# 用法示例：
#   .\scripts\sync_to_robot.ps1 -Dest "robot_user@192.168.31.201:/agibot/data/home/agi/bot_connect"
# 可选参数：
#   -Src  本地源目录，默认脚本所在仓库根
#   -RsyncPath 指定 rsync 可执行路径（若未在 PATH 中）
param(
  [Parameter(Mandatory = $true)]
  [string]$Dest,
  [string]$Src = "",
  [string]$RsyncPath = "rsync"
)

$ErrorActionPreference = "Stop"

if (-not $Src) {
  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
  $Src = Resolve-Path (Join-Path $scriptDir "..")
}

if (-not (Test-Path $Src)) {
  Write-Error "Source path not found: $Src"
  exit 1
}

Write-Host "[sync] SRC=$Src -> DEST=$Dest"

$exclude = @(
  "--exclude=backend/uploads/",
  "--exclude=frontend/node_modules/",
  "--exclude=.git/",
  "--exclude=.gitignore"
)

$args = @(
  "-av", "--delete"
) + $exclude + @(
  (Join-Path $Src ".") ,
  $Dest
)

try {
  & $RsyncPath @args
} catch {
  Write-Error "rsync failed: $($_.Exception.Message)"
  exit 1
}

Write-Host "sync done."
