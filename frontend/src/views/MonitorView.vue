<template>
  <section class="monitor-grid">
    <article class="card">
      <div class="card-head">
        <h3>从机摄像头</h3>
        <span class="pill">slave</span>
      </div>
      <StreamBox
        v-model:url="slaveUrl"
        :auto-url="slaveStream.autoUrl"
        :stream-info="slaveStream"
        placeholder="如 http(s)://host:8889/slave-01/whep 或 mjpg/hls 地址"
      />
    </article>

    <article class="card">
      <div class="card-head">
        <h3>主机摄像头</h3>
        <span class="pill">master</span>
      </div>
      <StreamBox
        v-model:url="masterUrl"
        :auto-url="masterStream.autoUrl"
        :stream-info="masterStream"
        placeholder="主机或额外机位流"
      />
    </article>

    <article class="card">
      <div class="card-head">
        <h3>自定义</h3>
        <span class="pill muted">debug</span>
      </div>
      <StreamBox v-model:url="customUrl" placeholder="任意可直接在浏览器播放的流" />
    </article>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useStore } from '../store'
import StreamBox from '../components/StreamBox.vue'

const { state } = useStore()

const slaveUrl = ref(load('monitor_slave') || '')
const masterUrl = ref(load('monitor_master') || '')
const customUrl = ref(load('monitor_custom') || '')

function normalizeStreamInfo(raw = {}) {
  const presets = Array.isArray(raw.presets) ? raw.presets : []
  const autoFromPreset = presets.length ? (presets[0].url || '') : ''
  return {
    autoUrl: raw.webrtc_whep_url || raw.webrtc_page_url || raw.auto_url || autoFromPreset || '',
    rtspUrl: raw.rtsp_url || '',
    pageUrl: raw.webrtc_page_url || '',
    hlsUrl: raw.hls_url || '',
    topic: raw.topic || '',
    preferredPlayer: raw.preferred_player || '',
    presets,
    enabled: Boolean(raw.enabled),
  }
}

const slaveStream = computed(() => {
  const robotId = state.controlTargetRobot
  return normalizeStreamInfo(state.robots?.[robotId]?.status?.streams || {})
})

const masterStream = computed(() => {
  const robotId = state.brainTargetRobot
  return normalizeStreamInfo(state.robots?.[robotId]?.status?.streams || {})
})

function load(key) {
  if (typeof localStorage === 'undefined') return ''
  return localStorage.getItem(key) || ''
}
function save(key, value) {
  if (typeof localStorage === 'undefined') return
  if (value) localStorage.setItem(key, value)
  else localStorage.removeItem(key)
}

;[['monitor_slave', slaveUrl], ['monitor_master', masterUrl], ['monitor_custom', customUrl]].forEach(([k, r]) => {
  watch(r, (v) => save(k, v))
})
</script>

<style scoped>
.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
</style>
