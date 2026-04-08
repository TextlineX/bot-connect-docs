<template>
  <section class="audio-stage">
    <div class="gear" @click="showSettings = !showSettings">⚙️</div>
    <div v-if="showSettings" class="settings-card">
      <div class="settings-head">
        <span>录音设置</span>
        <button class="mini-btn ghost" @click="showSettings=false">关闭</button>
      </div>
      <div class="field">
        <label>分片时长 (秒)</label>
        <input type="number" min="1" max="30" v-model.number="chunkSeconds" />
      </div>
    </div>

    <div class="record-center">
      <div class="wave-button huge" @click="toggleRecord">
        <div class="label">{{ recording ? '录音中 · 点击停止并发送' : '点击开始录音' }}</div>
      </div>
      <div class="hint" style="margin-top:10px;">请在支持麦克风的浏览器、localhost 或 https 访问下使用。</div>
      <div class="hint warn" v-if="errorMsg">{{ errorMsg }}</div>
      <div class="hint" v-if="recording">状态：录音中</div>
    </div>

    <div class="floating upload">
      <input type="file" id="fileInput" class="file-input" accept="audio/*,video/webm" @change="onFile" />
      <label for="fileInput" class="mini-btn">上传音频</label>
    </div>

    <div class="floating recent">
      <div class="mini-card">
        <div class="mini-head">
          <span>最近音频</span>
          <button class="mini-btn ghost" @click="state.audio=[]">清空</button>
        </div>
        <div class="mini-list">
          <div v-for="(a,idx) in state.audio.slice(0,4)" :key="idx" class="mini-item">
            <span class="dot"></span>
            <span class="time">{{ a.ts }}</span>
          </div>
          <div v-if="!state.audio.length" class="hint small">暂无</div>
        </div>
      </div>
    </div>
  </section>

  <div v-if="uploading" class="overlay">
    <div class="modal">
      <div class="spinner"></div>
      <div class="modal-title">正在上传并分片</div>
      <div class="modal-tip">{{ uploadMessage }}</div>
      <div class="bar">
        <div class="bar-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../store'

const { state, send } = useStore()
const recording = ref(false)
const showSettings = ref(false)
const chunkSeconds = ref(5)
let mediaRecorder = null
let stream = null
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadMessage = ref('准备中')
const errorMsg = ref('')
const mimeType = (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported('audio/webm;codecs=opus'))
  ? 'audio/webm;codecs=opus'
  : undefined

async function toggleRecord() {
  if (recording.value) {
    stopRecord()
  } else {
    await startRecord()
  }
}

async function startRecord() {
  try {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      errorMsg.value = '当前环境不支持 getUserMedia（请用 Chrome/Edge 且使用 localhost/https 打开页面）'
      recording.value = false
      return
    }
    errorMsg.value = ''
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        noiseSuppression: true,
        echoCancellation: true,
      }
    })
    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
    mediaRecorder.ondataavailable = onChunk
    mediaRecorder.start(chunkSeconds.value * 1000) // 每 chunkSeconds 一个分片
    recording.value = true
  } catch (e) {
    console.error('录音失败', e)
    errorMsg.value = '录音失败：' + (e.message || e.name || '未知错误')
    recording.value = false
  }
}

function stopRecord() {
  try {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
    if (stream) stream.getTracks().forEach(t => t.stop())
  } catch (e) { /* ignore */ }
  recording.value = false
  mediaRecorder = null
  stream = null
}

function onChunk(evt) {
  const blob = evt.data
  if (!blob || !blob.size || blob.size < 2000) { // 太小当作空
    return
  }
  if (!state.connected) {
    errorMsg.value = '未连接后端，无法发送音频'
    return
  }
  const reader = new FileReader()
  reader.onloadend = () => {
    chunkAndSend(reader.result, blob.type || 'audio/webm')
  }
  reader.readAsArrayBuffer(blob)
}

function onFile(e) {
  const file = e.target.files?.[0]
  if (!file || !state.connected) return
  uploading.value = true
  uploadMessage.value = '读取文件...'
  uploadProgress.value = 2
  file.arrayBuffer()
    .then(buf => {
      const total = Math.ceil(buf.byteLength / MAX_CHUNK)
      chunkAndSend(buf, file.type || 'audio/webm', (idx) => {
        uploadProgress.value = Math.min(100, Math.round((idx / total) * 100))
        uploadMessage.value = `分片 ${idx}/${total}`
      })
      uploadMessage.value = '完成'
      uploadProgress.value = 100
      setTimeout(() => uploading.value = false, 400)
    })
    .catch(err => {
      console.error('文件读取失败', err)
      uploadMessage.value = '读取失败'
      setTimeout(() => uploading.value = false, 800)
    })
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer)
  const chunk = 0x8000
  let binary = ''
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk))
  }
  return btoa(binary)
}

const MAX_CHUNK = 512 * 1024 // 512KB
function chunkAndSend(buffer, mime, onProgress) {
  const bytes = new Uint8Array(buffer)
  const step = MAX_CHUNK
  let sent = 0
  for (let i = 0; i < bytes.length; i += step) {
    const slice = bytes.subarray(i, i + step)
    const b64 = arrayBufferToBase64(slice.buffer)
    send({
      type: 'audio_upload',
      robot_id: state.robotId,
      target_robot: state.targetRobot,
      payload: {
        mime: mime || 'audio/webm',
        data: b64,
      },
      ts: Date.now()/1000,
    })
    sent += 1
    if (onProgress) onProgress(sent)
  }
}
</script>

<style scoped>
.audio-stage {
  position: relative;
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.record-center { text-align: center; }
.wave-button {
  width: 280px; height: 280px; border-radius: 50%;
  border: 2px solid rgba(30,215,96,0.6);
  background: radial-gradient(circle at 30% 30%, rgba(30,215,96,0.22), rgba(18,18,18,0.55));
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden; cursor: pointer;
  box-shadow: 0 24px 55px rgba(0,0,0,0.5), 0 0 0 12px rgba(30,215,96,0.08);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.wave-button:hover { transform: scale(1.03); box-shadow: 0 34px 70px rgba(0,0,0,0.6), 0 0 0 14px rgba(30,215,96,0.16); }
.wave-button.huge { font-size: 18px; color: #fff; }
.wave-button .label {
  font-weight: 700;
  letter-spacing: 0.8px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
  position: relative;
  z-index: 2;
}
.wave-button::after {
  content: ""; position: absolute; inset: -20%;
  background-image: repeating-linear-gradient(
    -45deg,
    rgba(30,215,96,0.24) 0, rgba(30,215,96,0.24) 12px,
    transparent 12px, transparent 28px
  );
  animation: wave 1.8s linear infinite;
  opacity: 0.55;
  z-index: 1;
}
@keyframes wave { from { background-position: 0 0; } to { background-position: 56px 0; } }

.floating { position: absolute; z-index: 10; }
.floating.upload { left: 20px; bottom: 20px; }
.floating.recent { right: 20px; bottom: 20px; }

.file-input { display: none; }
.mini-btn {
  display: inline-block;
  padding: 10px 14px;
  border-radius: var(--radius-btn);
  border: 1px solid #111;
  background: #1f1f1f;
  cursor: pointer;
  font-weight: 600;
}
.mini-btn.ghost { background: transparent; }

.mini-card {
  width: 200px;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  background: rgba(21, 19, 19, 0.46);
  box-shadow: 0 12px 30px rgba(17,17,17,0.12);
}
.mini-head { display:flex; justify-content:space-between; align-items:center; font-size:13px; }
.mini-list { margin-top:8px; display:grid; gap:6px; }
.mini-item { display:flex; gap:6px; align-items:center; font-size:12px; color: var(--text); }
.mini-item .dot { width:6px; height:6px; border-radius:999px; background: var(--accent); }
.hint.small { font-size:12px; }
.hint.warn { color: #ff9d76; }

.hero-actions { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }

.gear {
  position: absolute;
  top: 16px;
  right: 16px;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.8;
}
.settings-card {
  position: absolute;
  top: 40px;
  right: 16px;
  width: 220px;
  padding: 12px;
  border-radius: 10px;
  background: rgba(24,24,24,0.95);
  border: 1px solid var(--border);
  box-shadow: 0 10px 26px rgba(0,0,0,0.4);
  z-index: 20;
}
.settings-head { display:flex; justify-content:space-between; align-items:center; color:#fff; margin-bottom:8px; }

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  backdrop-filter: blur(4px);
}
.modal {
  width: 260px;
  padding: 18px;
  border-radius: 16px;
  background: linear-gradient(145deg, #0f1114, #111820);
  border: 1px solid rgba(255,255,255,0.06);
  box-shadow: 0 20px 60px rgba(0,0,0,0.55);
  text-align: center;
  color: #e6e6e6;
}
.modal-title { font-weight: 700; margin-top: 4px; }
.modal-tip { margin-top: 6px; font-size: 13px; opacity: 0.85; }
.bar {
  margin-top: 12px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #1ed760, #65ffa5);
  width: 0%;
  transition: width 0.15s ease;
}
.spinner {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 3px solid rgba(255,255,255,0.12);
  border-top-color: #1ed760;
  margin: 0 auto 8px;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
