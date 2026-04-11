<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="dot"></span>
        <div>
          <div class="eyebrow">BOT CONNECT</div>
          <div class="title">控制舱</div>
        </div>
      </div>
      <nav class="nav">
        <RouterLink v-for="r in routes" :key="r.path" :to="r.path" class="nav-btn" active-class="active">
          {{ r.label }}
        </RouterLink>
      </nav>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { routes as rawRoutes } from './router'
import { RouterLink, RouterView } from 'vue-router'
import { useStore } from './store'
import { computed } from 'vue'

const { state } = useStore()

const routes = computed(() => rawRoutes
  .filter(r => r.name)
  .filter(r => featureEnabled(r.name))
  .map(r => ({ path: r.path, label: r.name })))

function featureEnabled(name) {
  const map = {
    'Dashboard': 'showDashboard',
    '控制': 'showControl',
    'TTS': 'showTTS',
    'ASR': 'showASR',
    'AI': 'showAI',
    '音频': 'showAudio',
    '监控': 'showMonitor',
    '日志': 'showLogs',
    '设置': 'showSettings',
  }
  const key = map[name]
  if (!key) return true
  return state.featureFlags?.[key] !== false
}
</script>
