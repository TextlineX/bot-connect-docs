<template>
  <section class="monitor-grid">
    <article class="card">
      <div class="card-head">
        <h3>从机摄像头</h3>
        <span class="pill">slave</span>
      </div>
      <StreamBox v-model:url="slaveUrl" placeholder="如 http(s)/mjpg/flv/hls 地址" />
    </article>

    <article class="card">
      <div class="card-head">
        <h3>主机摄像头</h3>
        <span class="pill">master</span>
      </div>
      <StreamBox v-model:url="masterUrl" placeholder="主机或额外机位流" />
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
import { ref, watch } from 'vue'

const slaveUrl = ref(load('monitor_slave') || '')
const masterUrl = ref(load('monitor_master') || '')
const customUrl = ref(load('monitor_custom') || '')

function load(key) {
  if (typeof localStorage === 'undefined') return ''
  return localStorage.getItem(key) || ''
}
function save(key, value) {
  if (typeof localStorage === 'undefined') return
  if (value) localStorage.setItem(key, value)
  else localStorage.removeItem(key)
}

[ ['monitor_slave', slaveUrl], ['monitor_master', masterUrl], ['monitor_custom', customUrl] ].forEach(([k, r]) => {
  watch(r, (v) => save(k, v))
})
</script>

<script>
export default {
  components: {
    StreamBox: {
      props: {
        url: { type: String, default: '' },
        placeholder: { type: String, default: '' },
      },
      emits: ['update:url'],
      computed: {
        isVideo() {
          const u = (this.url || '').toLowerCase()
          return u.startsWith('http') && (u.includes('.m3u8') || u.includes('.mp4') || u.includes('.webm'))
        },
        isMjpg() {
          const u = (this.url || '').toLowerCase()
          return u.includes('mjpg') || u.includes('mjpeg')
        },
      },
      methods: {
        onInput(e) { this.$emit('update:url', e.target.value.trim()) },
      },
      template: `
        <div class="stream-box">
          <input class="url" :placeholder="placeholder" :value="url" @input="onInput" />
          <div class="preview" v-if="url">
            <video v-if="isVideo" :src="url" autoplay playsinline controls muted></video>
            <img v-else-if="isMjpg" :src="url" alt="mjpg" />
            <iframe v-else :src="url" frameborder="0" allow="autoplay" referrerpolicy="no-referrer"></iframe>
          </div>
          <div class="hint" v-else>输入可直接在浏览器播放的 http(s)/m3u8/mp4/webm/mjpg/flv.js 等流地址</div>
        </div>
      `,
    },
  },
}
</script>

<style scoped>
.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
.stream-box { display: grid; gap: 10px; }
.url {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: rgba(20,20,20,0.7);
  color: var(--text);
}
.preview {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: #0e0e0e;
  border: 1px solid var(--border);
  box-shadow: 0 12px 32px rgba(0,0,0,0.35);
}
.preview video,
.preview img,
.preview iframe {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  background: #000;
}
.hint { font-size: 12px; color: #9aa0a6; }
</style>
