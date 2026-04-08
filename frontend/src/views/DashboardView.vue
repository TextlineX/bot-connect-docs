<template>
  <section class="grid">
    <article class="card">
      <div class="card-head">
        <h3>状态 · 主机</h3>
        <span class="pill" :class="state.connected ? 'accent' : ''">{{ state.connected ? 'online' : 'offline' }}</span>
      </div>
      <div class="metrics">
        <div class="metric"><div class="label">连接</div><div class="value">{{ state.connected ? '已连接' : '未连接' }}</div></div>
        <div class="metric"><div class="label">最近心跳</div><div class="value">{{ lastHeartbeat }}</div></div>
        <div class="metric"><div class="label">最近 ASR</div><div class="value">{{ lastAsr }}</div></div>
      </div>
    </article>

    <article class="card">
      <div class="card-head">
        <h3>状态 · 从机</h3>
        <span class="pill muted">监听</span>
      </div>
      <div class="metrics">
        <div class="metric"><div class="label">在线机器人</div><div class="value">{{ onlineCount }}</div></div>
        <div class="metric"><div class="label">目标 robot</div><div class="value">{{ state.targetRobot }}</div></div>
        <div class="metric"><div class="label">上次消息</div><div class="value">{{ lastMsg }}</div></div>
      </div>
    </article>

    <article class="card wide">
      <div class="card-head">
        <h3>高级连接设置</h3>
        <button class="btn ghost small" @click="showAdvanced = !showAdvanced">{{ showAdvanced ? '收起' : '展开' }}</button>
      </div>
      <div v-if="showAdvanced">
        <div class="field">
          <label>WebSocket 地址</label>
          <input v-model="state.wsUrl" :placeholder="defaultWs" />
        </div>
        <div class="field">
          <label>快速选择</label>
          <select v-model="state.wsUrl">
            <option v-for="p in presets" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </div>
        <div class="field duo">
          <div><label>本端 robot_id</label><input v-model="state.robotId" placeholder="controller" /></div>
          <div><label>目标 robot_id</label><input v-model="state.targetRobot" placeholder="master-01" /></div>
        </div>
        <div class="field">
          <label>角色</label>
          <select v-model="state.role">
            <option value="controller">controller</option>
            <option value="master">master</option>
            <option value="slave">slave</option>
          </select>
        </div>
        <div class="field">
          <label><input type="checkbox" v-model="state.autoReconnect" /> 自动重连</label>
        </div>
        <div class="hero-actions" style="gap:8px;">
          <button class="btn dark" @click="connect" :disabled="state.connected">连接</button>
          <button class="btn ghost" @click="disconnect" :disabled="!state.connected">断开</button>
          <span class="badge" :class="state.connected ? 'green' : 'red'">
            {{ state.connected ? '已连接' : '未连接' }}
          </span>
        </div>
        <div class="hint" style="margin-top:8px;">WSL 访问宿主请用 172.19.0.1；浏览器本机用 127.0.0.1。</div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '../store'
import { routes as routeDefs } from '../router'

const { state, connect, disconnect, presets } = useStore()
const showAdvanced = ref(false)

const defaultWs = computed(() => {
  const host = window.location.hostname || '127.0.0.1'
  return `ws://${host}:8765`
})
const lastHeartbeat = computed(() => {
  const ts = state.online[state.robotId]
  return ts ? new Date(ts).toLocaleTimeString() : '—'
})
const lastAsr = computed(() => state.asr[0] ? state.asr[0].slice(0, 50) : '—')
const lastMsg = computed(() => state.logs[0]?.msg?.slice(0, 32) || '—')
const onlineCount = computed(() => Object.keys(state.online).length)

onMounted(() => {
  if (!state.wsUrl) state.wsUrl = defaultWs.value
})
</script>
