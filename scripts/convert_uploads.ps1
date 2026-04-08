param(
  [string]$InputDir = "H:\Project\Bot\bot_connect\backend\uploads",
  [string]$OutputDir = "H:\Project\Bot\bot_connect\backend\uploads\wav"
)

if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null }

Get-ChildItem -Path $InputDir -File |
  Where-Object { $_.Extension -in ".webm", ".raw" } |
  ForEach-Object {
    $out = Join-Path $OutputDir ($_.BaseName + ".wav")
    if ($_.Extension -eq ".webm") {
      ffmpeg -y -i $_.FullName -ar 16000 -ac 1 -acodec pcm_s16le $out | Out-Null
    } else {
      ffmpeg -y -f s16le -ar 16000 -ac 1 -i $_.FullName $out | Out-Null
    }
    Write-Host "=> $out"
  }
