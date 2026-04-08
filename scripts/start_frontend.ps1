param(
  [int]$Port = 5173
)
cd H:\Project\Bot\bot_connect\frontend
Write-Host "[start_frontend] Vite dev server on port $Port"
npm run dev -- --host --port $Port
