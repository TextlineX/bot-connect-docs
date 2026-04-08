<template>
  <section class="card">
    <div class="card-head">
      <h3>TTS 对话</h3>
      <span class="pill">exec.tts</span>
    </div>
    <div class="chat-window">
      <div v-for="(m,idx) in messages" :key="idx" :class="['bubble', m.role === 'you' ? 'you' : 'bot']">
        <div class="meta">{{ m.role === 'you' ? '你' : '机器人' }} · {{ m.ts }}</div>
        <div class="text">{{ m.text }}</div>
      </div>
      <div v-if="!messages.length" class="hint">暂时没有消息</div>
    </div>
    <div class="composer">
      <textarea rows="3" v-model="ttsText" placeholder="输入要播报的内容..."></textarea>
      <div class="composer-actions">
        <button class="btn ghost small" @click="ttsText=''">清空</button>
        <button class="btn dark" @click="sendTts" :disabled="!state.connected">发送</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useStore } from '../store'

const { state, send } = useStore()
const ttsText = ref('你好，我是主机。')
const messages = ref([
  { role:'bot', text:'这里显示 TTS 回执或机器人回复。', ts: new Date().toLocaleTimeString() }
])

// 当有新的 TTS 回执 result 时，追加机器人消息
watch(() => state.results[0], (r) => {
  if (!r) return
  messages.value.push({ role:'bot', text:`回执: ${r.detail || ''} ok=${r.ok}`, ts: new Date().toLocaleTimeString() })
  if (messages.value.length > 200) messages.value.shift()
})

function sendTts() {
  if (!ttsText.value.trim()) return
  const msg = {
    type: 'exec',
    robot_id: state.robotId,
    target_robot: state.targetRobot,
    payload: { action: 'tts', text: ttsText.value },
    ts: Date.now() / 1000,
  }
  send(msg)
  messages.value.push({ role:'you', text: ttsText.value, ts: new Date().toLocaleTimeString() })
  if (messages.value.length > 200) messages.value.shift()
}
</script>

<style scoped>
.chat-window {
  border:1px solid var(--border);
  border-radius:12px;
  padding:12px;
  background:var(--bg);
  min-height:220px;
  max-height:360px;
  overflow:auto;
  display:flex;
  flex-direction:column;
  gap:10px;
}
.bubble {
  padding:10px 12px;
  border-radius:12px;
  max-width: 90%;
}
.bubble.you { background:#111; color:#fff; margin-left:auto; }
.bubble.bot { background:#1c1c1c; border:1px solid var(--border); }
.meta { font-size:12px; color:var(--muted); margin-bottom:4px; }
.text { white-space:pre-wrap; }
.composer { margin-top:12px; display:flex; flex-direction:column; gap:8px; }
.composer-actions { display:flex; gap:10px; justify-content:flex-end; }
</style>
