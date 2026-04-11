<template>
  <div class="webrtc-player">
    <video ref="videoRef" autoplay playsinline muted controls></video>
    <div v-if="statusText" class="overlay">{{ statusText }}</div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  url: { type: String, default: '' },
})

const videoRef = ref(null)
const statusText = ref('')
let reader = null
let pendingPromise = null

function normalizeWhepUrl(url) {
  const value = String(url || '').trim()
  if (!value) return ''
  if (value.toLowerCase().includes('/whep')) return value
  return `${value.replace(/\/+$/, '')}/whep`
}

function ensureReaderScript() {
  if (window.MediaMTXWebRTCReader) return Promise.resolve()
  if (pendingPromise) return pendingPromise

  pendingPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById('mediamtx-webrtc-reader')
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener('error', () => reject(new Error('reader.js load failed')), { once: true })
      return
    }

    const script = document.createElement('script')
    script.id = 'mediamtx-webrtc-reader'
    script.src = '/mediamtx-reader.js'
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('reader.js load failed'))
    document.head.appendChild(script)
  }).finally(() => {
    pendingPromise = null
  })

  return pendingPromise
}

function cleanup() {
  if (reader && typeof reader.close === 'function') {
    try { reader.close() } catch {}
  }
  reader = null
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

async function connect(url) {
  const whepUrl = normalizeWhepUrl(url)
  cleanup()
  if (!whepUrl) {
    statusText.value = ''
    return
  }

  statusText.value = 'WebRTC 连接中...'

  try {
    await ensureReaderScript()
    if (!window.MediaMTXWebRTCReader) {
      throw new Error('MediaMTX reader 不可用')
    }

    reader = new window.MediaMTXWebRTCReader({
      url: whepUrl,
      onError: (error) => {
        statusText.value = `WebRTC 出错：${error}`
      },
      onTrack: (event) => {
        const stream = event?.streams?.[0]
        if (videoRef.value && stream) {
          videoRef.value.srcObject = stream
          statusText.value = ''
        }
      },
    })
  } catch (error) {
    statusText.value = `WebRTC 初始化失败：${error?.message || error}`
  }
}

watch(
  () => props.url,
  (nextUrl) => { connect(nextUrl) },
  { immediate: true }
)

onBeforeUnmount(() => {
  cleanup()
})
</script>

<style scoped>
.webrtc-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
}

.webrtc-player video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  background: #000;
}

.overlay {
  position: absolute;
  inset: auto 12px 12px 12px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.55);
  color: #d7dde4;
  font-size: 12px;
  backdrop-filter: blur(6px);
}
</style>
