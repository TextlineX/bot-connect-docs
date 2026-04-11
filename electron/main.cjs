// Electron 主进程 - CommonJS
const { app, BrowserWindow, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

const ROOT = path.resolve(__dirname, '..')
const FRONTEND_DIST = path.join(ROOT, 'frontend', 'dist')
const IS_DEV = !app.isPackaged

let win = null

function findVitePort() {
  const viteConfigPath = path.join(ROOT, 'frontend', 'vite.config.js')
  if (fs.existsSync(viteConfigPath)) {
    const content = fs.readFileSync(viteConfigPath, 'utf-8')
    const m = content.match(/port:\s*(\d+)/)
    if (m) return parseInt(m[1])
  }
  return 5173
}

function startVite() {
  return new Promise((resolve, reject) => {
    const vitePort = findVitePort()
    const isWin = process.platform === 'win32'
    const viteBin = isWin ? 'vite.cmd' : 'vite'
    const viteScript = path.join(ROOT, 'frontend', 'node_modules', '.bin', viteBin)

    const args = ['--host', '0.0.0.0', '--port', String(vitePort)]
    if (isWin) args.unshift(viteScript)

    const proc = spawn(isWin ? viteScript : 'node', isWin ? args : [viteScript, ...args], {
      cwd: ROOT,
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: isWin,
      detached: false,
    })

    let resolved = false
    proc.stdout.on('data', (data) => {
      const line = data.toString()
      process.stdout.write('[vite] ' + line)
      if (!resolved && (line.includes('Local:') || line.includes('ready in'))) {
        resolved = true
        resolve(`http://localhost:${vitePort}`)
      }
    })
    proc.stderr.on('data', (data) => {
      process.stderr.write('[vite] ' + data.toString())
    })
    proc.on('error', reject)
    // 最多等 15 秒
    setTimeout(() => {
      if (!resolved) resolve(`http://localhost:${vitePort}`)
    }, 15000)
  })
}

function startBackend() {
  const serverPath = path.join(ROOT, 'backend', 'server.js')
  if (!fs.existsSync(serverPath)) {
    console.log('[electron] backend server.js not found, skipping')
    return
  }
  const isWin = process.platform === 'win32'
  const proc = spawn(isWin ? 'node.cmd' : 'node', [serverPath], {
    cwd: path.join(ROOT, 'backend'),
    stdio: 'inherit',
    shell: isWin,
    detached: false,
    env: { ...process.env },
  })
  proc.on('error', (e) => console.error('[electron] backend error:', e))
  console.log('[electron] backend started')
}

function createWindow(url) {
  win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Bot Connect',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  win.webContents.setWindowOpenHandler(({ url: u }) => {
    shell.openExternal(u)
    return { action: 'deny' }
  })

  if (url) {
    win.loadURL(url)
  } else {
    win.loadFile(path.join(FRONTEND_DIST, 'index.html'))
  }

  win.on('closed', () => { win = null })

  if (IS_DEV) {
    win.webContents.openDevTools()
  }

  console.log('[electron] window ready')
}

app.whenReady().then(async () => {
  if (!IS_DEV) {
    // 生产模式：直接加载构建产物，同时启动后端
    createWindow(null)
    startBackend()
    return
  }

  // 开发模式：启动 vite dev server
  try {
    const url = await startVite()
    createWindow(url)
    // 如需同时调试后端，取消下面这行注释
    // startBackend()
  } catch (e) {
    console.error('[electron] vite start failed:', e)
    createWindow(null)
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow(null)
})
