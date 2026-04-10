<template>
  <section class="card">
    <div class="card-head">
      <h3>日志</h3>
      <div class="card-actions filters">
        <label class="switch">
          <input type="checkbox" v-model="verboseEnabled">
          <span>显示全部 WS 细节</span>
        </label>

        <div class="btn-group">
          <button v-for="d in dirs" :key="d.value" :class="['chip-btn', {active: filterDir === d.value}]" @click="filterDir = d.value">{{ d.label }}</button>
        </div>
        <div class="btn-group">
          <button v-for="t in types" :key="t.value" :class="['chip-btn', {active: filterType === t.value}]" @click="filterType = t.value">{{ t.label }}</button>
        </div>
        <div class="btn-group">
          <button v-for="r in roles" :key="r.value" :class="['chip-btn', {active: filterRole === r.value}]" @click="filterRole = r.value">{{ r.label }}</button>
        </div>
        <div class="btn-group scrollable">
          <button v-for="m in msgTypes" :key="m.value" :class="['chip-btn', {active: filterMsgType === m.value}]" @click="filterMsgType = m.value">{{ m.label }}</button>
        </div>

        <input class="compact" v-model="filterRobot" placeholder="robot_id 包含..." />
        <input class="compact" v-model="filterAction" placeholder="action" />
        <input class="compact" v-model="filterKeyword" placeholder="关键词" />
        <label class="switch">
          <input type="checkbox" v-model="prettyView">
          <span>提取 JSON 关键信息</span>
        </label>
        <button class="btn ghost small" @click="state.logs=[]">清空</button>
      </div>
    </div>
    <div class="log list">
      <div v-for="(l,idx) in filtered" :key="idx" class="log-card">
        <div class="meta">
          <span class="chip" :class="chipClass(l)">{{ l.dir || l.type }}</span>
          <span class="chip muted" v-if="l.msg_type">{{ l.msg_type }}</span>
          <span class="chip ghost" v-if="l.robot_id">{{ l.robot_id }}</span>
          <span class="chip ghost" v-if="l.source_role">{{ l.source_role }}</span>
          <span class="chip ghost" v-if="l.target_robot">→ {{ l.target_robot }}</span>
          <span>{{ l.ts }}</span>
        </div>
        <div class="body">
          <template v-if="prettyView">
            <div v-if="isJson(l.msg)" class="json-compact">
              <div class="json-summary" v-if="summary(l.msg)">{{ summary(l.msg) }}</div>
              <span class="json-key">type</span>: {{ fieldOr(jsonField(l.msg, 'type')) }},
              <span class="json-key">robot</span>: {{ fieldOr(jsonField(l.msg, 'robot_id')) }},
              <span class="json-key">source</span>: {{ fieldOr(jsonField(l.msg, 'source_robot_id')) }},
              <span class="json-key">target</span>: {{ fieldOr(jsonField(l.msg, 'target_robot')) }},
              <span class="json-key">action</span>: {{ fieldOr(jsonField(l.msg, 'action') || jsonField(l.msg, 'payload.action')) }},
              <span class="json-key">detail</span>: {{ fieldOr(jsonField(l.msg, 'detail')) }},
              <span class="json-key">ok</span>: {{ fieldOr(jsonField(l.msg, 'ok')) }},
              <span class="json-key">config_v</span>: {{ fieldOr(jsonField(l.msg, 'config_version')) }}
              <details>
                <summary class="hint">展开 JSON</summary>
                <pre>{{ pretty(l.msg) }}</pre>
              </details>
            </div>
            <div v-else>{{ l.msg }}</div>
          </template>
          <template v-else>
            {{ l.msg }}
          </template>
        </div>
      </div>
      <div v-if="!filtered.length" class="hint">暂无日志</div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from '../store'

const { state } = useStore()
const filterType = ref('all')
const filterDir = ref('all')
const filterRole = ref('all')
const filterRobot = ref('')
const filterMsgType = ref('all')
const filterAction = ref('')
const filterKeyword = ref('')
const verboseEnabled = ref(false)
const prettyView = ref(true)

const dirs = [
  { value: 'all', label: '全部方向' },
  { value: 'in', label: '收' },
  { value: 'out', label: '发' },
  { value: 'sys', label: '系统' },
]
const types = [
  { value: 'all', label: '全部类型' },
  { value: 'info', label: 'info' },
  { value: 'warn', label: 'warn' },
  { value: 'error', label: 'error' },
  { value: 'send', label: 'send' },
  { value: 'recv', label: 'recv' },
]
const roles = [
  { value: 'all', label: '全部角色' },
  { value: 'master', label: 'master' },
  { value: 'slave', label: 'slave' },
  { value: 'controller', label: 'controller' },
  { value: 'server', label: 'server' },
]
const msgTypes = [
  { value: 'all', label: '全部 msg.type' },
  { value: 'status', label: 'status' },
  { value: 'capabilities', label: 'capabilities' },
  { value: 'audio_upload', label: 'audio_upload' },
  { value: 'asr_text', label: 'asr_text' },
  { value: 'ai_result', label: 'ai_result' },
  { value: 'result', label: 'result' },
  { value: 'exec', label: 'exec' },
  { value: 'cmd_vel', label: 'cmd_vel' },
  { value: 'config_sync', label: 'config_sync' },
  { value: 'config_sync_ack', label: 'config_ack' },
  { value: 'config_update', label: 'config_update' },
  { value: 'hello', label: 'hello' },
  { value: 'open', label: 'open' },
  { value: 'other', label: 'other' },
]

const filtered = computed(() => {
  const robotKey = filterRobot.value.trim().toLowerCase()
  const msgTypeKey = filterMsgType.value
  const actionKey = filterAction.value.trim().toLowerCase()
  const keyword = filterKeyword.value.trim().toLowerCase()
  return state.logs.filter((l) => {
    if (!verboseEnabled.value) {
      const noisy = ['ping', 'pong', 'status', 'capabilities']
      if (noisy.includes(l.msg_type)) return false
      if (l.dir === 'in' && l.type === 'info' && l.msg_type === 'open') return false
    }
    if (filterType.value !== 'all' && l.type !== filterType.value) return false
    if (filterDir.value !== 'all' && l.dir !== filterDir.value) return false
    if (filterRole.value !== 'all') {
      const roles = [l.source_role, l.target_role, l.role].filter(Boolean).map(r => String(r).toLowerCase())
      if (!roles.includes(filterRole.value)) return false
    }
    if (robotKey) {
      const ids = [l.robot_id, l.source_robot_id, l.target_robot].filter(Boolean).map(r => String(r).toLowerCase())
      if (!ids.some(id => id.includes(robotKey))) return false
    }
    if (msgTypeKey !== 'all') {
      const mt = String(l.msg_type || '').toLowerCase()
      if (msgTypeKey === 'other') {
        const common = msgTypes.filter(m => m.value !== 'all' && m.value !== 'other').map(m => m.value)
        if (common.includes(mt)) return false
      } else if (mt !== msgTypeKey) return false
    }
    if (actionKey) {
      const act = String(l.action || '').toLowerCase()
      if (!act.includes(actionKey)) return false
    }
    if (keyword) {
      const blob = (l.msg || '').toLowerCase()
      if (!blob.includes(keyword)) return false
    }
    return true
  })
})

function chipClass(l) {
  if (l.type === 'send') return 'send'
  if (l.type === 'recv') return 'recv'
  if (l.type === 'error') return 'error'
  return ''
}

function isJson(text) {
  if (typeof text !== 'string') return false
  const t = text.trim()
  if (!(t.startsWith('{') || t.startsWith('['))) return false
  try { JSON.parse(t); return true } catch { return false }
}

function parseJson(text) {
  if (!isJson(text)) return null
  try { return JSON.parse(text) } catch { return null }
}

function jsonField(text, path) {
  const obj = parseJson(text)
  if (!obj) return null
  const parts = path.split('.')
  let cur = obj
  for (const p of parts) {
    if (cur && Object.prototype.hasOwnProperty.call(cur, p)) {
      cur = cur[p]
    } else {
      return null
    }
  }
  if (cur === undefined || cur === null) return null
  if (typeof cur === 'object') return JSON.stringify(cur)
  return String(cur)
}

function pretty(text) {
  const obj = parseJson(text)
  if (!obj) return String(text)
  try { return JSON.stringify(obj, null, 2) } catch { return String(text) }
}

function fieldOr(value, placeholder = '-') {
  if (value === undefined || value === null || value === '') return placeholder
  return value
}

function summary(text) {
  const obj = parseJson(text)
  if (!obj) return ''
  const type = obj.type || '消息'
  const action = obj.action || (obj.payload && obj.payload.action) || ''
  const from = obj.source_robot_id || obj.robot_id || '-'
  const fromRole = obj.source_role || obj.role || ''
  const to = obj.target_robot || '-'
  const ok = obj.ok
  const detail = obj.detail || ''
  const parts = []
  parts.push(`【${translateType(type)}${action ? '·' + action : ''}】`)
  parts.push(`来自 ${from}${fromRole ? '（' + fromRole + '）' : ''}`)
  parts.push(`→ 目标 ${to}`)
  if (ok === true) parts.push('成功')
  else if (ok === false) parts.push('失败')
  if (detail) parts.push(`详情: ${detail}`)
  return parts.join(' | ')
}

function translateType(t) {
  const map = {
    result: '结果',
    asr_text: 'ASR',
    ai_result: 'AI',
    exec: '指令',
    cmd_vel: '运动',
    audio_upload: '音频',
    status: '状态',
    capabilities: '能力',
    config_sync: '配置',
    config_update: '配置更新',
  }
  return map[t] || t
}
</script>

<style scoped>
.log .meta { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.chip { padding:2px 8px; border-radius:999px; background:rgba(255,255,255,0.08); font-size:12px; }
.chip.send { background:#1e90ff2b; color:#8bc1ff; }
.chip.recv { background:#10b9812b; color:#86efac; }
.chip.error { background:#ef44442b; color:#fca5a5; }
.chip.muted { background:rgba(255,255,255,0.05); color:#d1d5db; }
.chip.ghost { background:rgba(255,255,255,0.03); color:#cbd5e1; }
.filters { flex-wrap: wrap; gap:6px; }
.btn-group { display:flex; gap:6px; flex-wrap:wrap; }
.btn-group.scrollable { max-width:100%; overflow-x:auto; }
.chip-btn {
  border:1px solid var(--border);
  border-radius:999px;
  padding:6px 10px;
  background:rgba(255,255,255,0.05);
  color:#dfe7f3;
  font-size:12px;
  cursor:pointer;
  transition: all 120ms ease;
  margin-bottom: 4px;
}
.chip-btn:hover { background:rgba(255,255,255,0.12); }
.chip-btn.active { background:var(--accent); color:#000; border-color:var(--accent); box-shadow:0 4px 14px rgba(30,215,96,0.4); }
input.compact { width: 140px; padding: 6px 8px; }
.switch { display:flex; align-items:center; gap:6px; font-size:12px; opacity:0.8; }
.switch input { width:16px; height:16px; }
.json-compact { font-family: ui-monospace; font-size: 12px; color:#dce3ef; line-height:1.6; }
.json-key { color:#9fb3ff; }
.json-summary { font-weight:700; color:#fff; margin-bottom:4px; }
.json-compact details { margin-top:6px; }
.json-compact pre { background:rgba(255,255,255,0.04); padding:8px; border-radius:8px; border:1px solid var(--border); }
</style>
