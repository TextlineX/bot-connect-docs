import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

// 尝试加载本地自签证书（frontend/certs/dev.crt, dev.key），存在则启用 https
function loadHttps() {
  const crt = path.resolve(__dirname, 'certs/dev.crt')
  const key = path.resolve(__dirname, 'certs/dev.key')
  if (fs.existsSync(crt) && fs.existsSync(key)) {
    return { cert: fs.readFileSync(crt), key: fs.readFileSync(key) }
  }
  return undefined
}

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // 有 cert/key 用它；否则退回 http（避免老设备不支持自签 TLS）
    https: loadHttps() || false,
    strictPort: true
  }
})
