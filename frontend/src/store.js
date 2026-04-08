import { reactive, computed } from 'vue'

const state = reactive({
  wsUrl: '',
  robotId: 'controller',
  targetRobot: 'master-01',
  role: 'controller',          // controller / master / slave
  connected: false,
  autoReconnect: true,
  ws: null,
  reconnectTimer: null,
  logs: [],          // {ts,type,dir,msg}
  results: [],       // TTS 回执
  asr: [],           // asr_text
  audio: [],         // 上传/录制记录
  online: {},        // robot_id -> status ts
})

const CFG_KEY = 'bot_connect_cfg_v2'

function loadConfig() {
  try {
    const raw = localStorage.getItem(CFG_KEY)
    if (!raw) return
    const cfg = JSON.parse(raw)
    state.wsUrl = cfg.wsUrl || state.wsUrl
    state.robotId = cfg.robotId || state.robotId
    state.targetRobot = cfg.targetRobot || state.targetRobot
    state.role = cfg.role || state.role
    state.autoReconnect = cfg.autoReconnect ?? state.autoReconnect
  } catch (e) {
    // ignore parse errors
  }
}

function saveConfig() {
  const cfg = {
    wsUrl: state.wsUrl,
    robotId: state.robotId,
    targetRobot: state.targetRobot,
    role: state.role,
    autoReconnect: state.autoReconnect,
  }
  localStorage.setItem(CFG_KEY, JSON.stringify(cfg))
}

function nowTs() { return new Date().toLocaleTimeString() }
function pushLog(entry) {
  state.logs.unshift({ ts: nowTs(), ...entry })
  if (state.logs.length > 1000) state.logs.pop()
}

function connect(urlOverride) {
  const url = urlOverride || state.wsUrl
  if (!url) return pushLog({ type: 'error', dir: 'out', msg: '缺少 WS 地址' })
  if (state.connected && state.ws) return
  saveConfig()
  try {
    state.ws = new WebSocket(url)
    state.ws.onopen = () => {
      state.connected = true
      clearTimeout(state.reconnectTimer)
      pushLog({ type: 'info', dir: 'sys', msg: '已连接' })
      const hello = { type: 'hello', robot_id: state.robotId, ts: Date.now()/1000 }
      state.ws.send(JSON.stringify(hello))
      pushLog({ type: 'send', dir: 'out', msg: JSON.stringify(hello) })
    }
    state.ws.onclose = (e) => {
      state.connected = false
      pushLog({ type: 'warn', dir: 'sys', msg: '连接关闭 ' + (e.reason || '') })
      if (state.autoReconnect) {
        clearTimeout(state.reconnectTimer)
        state.reconnectTimer = setTimeout(() => connect(), 3000)
      }
    }
    state.ws.onerror = (e) => {
      pushLog({ type: 'error', dir: 'sys', msg: e?.message || 'ws error' })
    }
    state.ws.onmessage = (e) => {
      let data = null
      try { data = JSON.parse(e.data) } catch { data = null }
      pushLog({ type: 'recv', dir: 'in', msg: e.data })
      if (!data) return
      if (data.type === 'result') {
        state.results.unshift({ ts: nowTs(), ok: data.ok, detail: data.detail ?? '' })
        if (state.results.length > 200) state.results.pop()
      } else if (data.type === 'asr_text') {
        const txt = (data.text || '').trim()
        if (txt) {
          state.asr.unshift(`${nowTs()} | ${txt}`)
          if (state.asr.length > 500) state.asr.pop()
        }
      } else if (data.type === 'audio_saved' || data.type === 'audio_available') {
        state.audio.unshift({ ts: nowTs(), detail: data })
        if (state.audio.length > 200) state.audio.pop()
      }
      if (data.robot_id) state.online[data.robot_id] = Date.now()
    }
  } catch (e) {
    pushLog({ type: 'error', dir: 'sys', msg: e.message })
  }
}

function disconnect() {
  clearTimeout(state.reconnectTimer)
  if (state.ws) state.ws.close()
  state.ws = null
  state.connected = false
}

function send(obj) {
  if (!state.connected || !state.ws) {
    pushLog({ type: 'warn', dir: 'out', msg: '未连接，无法发送' })
    return
  }
  state.ws.send(JSON.stringify(obj))
  pushLog({ type: 'send', dir: 'out', msg: JSON.stringify(obj) })
}

const presets = computed(() => {
  const host = window.location.hostname || '127.0.0.1'
  return [
    { label: '本机回环', value: 'ws://127.0.0.1:8765' },
    { label: '当前主机', value: `ws://${host}:8765` },
    { label: 'WSL 宿主网关', value: 'ws://172.19.0.1:8765' },
  ]
})

export function useStore() {
  return { state, connect, disconnect, send, presets, loadConfig, saveConfig }
}

// 初始化
if (typeof window !== 'undefined') {
  loadConfig()
}
// 刷新后自动重连
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    if (state.autoReconnect && state.wsUrl) {
      setTimeout(() => connect(), 300)
    }
  })
}
