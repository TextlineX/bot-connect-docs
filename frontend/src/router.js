import { createRouter, createWebHashHistory } from 'vue-router'

import DashboardView from './views/DashboardView.vue'
import ControlView from './views/ControlView.vue'
import TtsView from './views/TtsView.vue'
import AudioView from './views/AudioView.vue'
import AsrView from './views/AsrView.vue'
import LogsView from './views/LogsView.vue'
import SettingsView from './views/SettingsView.vue'
import AiDebugView from './views/AiDebugView.vue'
import MonitorView from './views/MonitorView.vue'

export const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/control', name: '控制', component: ControlView },
  { path: '/tts', name: 'TTS', component: TtsView },
  { path: '/asr', name: 'ASR', component: AsrView },
  { path: '/ai', name: 'AI', component: AiDebugView },
  { path: '/audio', name: '音频', component: AudioView },
  { path: '/monitor', name: '监控', component: MonitorView },
  { path: '/logs', name: '日志', component: LogsView },
  { path: '/settings', name: '设置', component: SettingsView },
]

export function createAppRouter() {
  return createRouter({
    history: createWebHashHistory(),
    routes,
  })
}
