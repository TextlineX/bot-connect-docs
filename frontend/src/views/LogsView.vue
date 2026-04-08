<template>
  <section class="card">
    <div class="card-head">
      <h3>日志</h3>
      <div class="card-actions" style="display:flex; gap:8px; align-items:center;">
        <select v-model="filterType">
          <option value="all">全部</option>
          <option value="recv">收</option>
          <option value="send">发</option>
          <option value="error">错误</option>
        </select>
        <button class="btn ghost small" @click="state.logs=[]">清空</button>
      </div>
    </div>
    <div class="log list">
      <div v-for="(l,idx) in filtered" :key="idx" class="log-card">
        <div class="meta">
          <span class="chip" :class="chipClass(l)">{{ l.type }}</span>
          <span>{{ l.ts }}</span>
        </div>
        <div class="body">{{ l.msg }}</div>
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

const filtered = computed(() => {
  if (filterType.value === 'all') return state.logs
  return state.logs.filter(l => l.type === filterType.value)
})

function chipClass(l) {
  if (l.type === 'send') return 'send'
  if (l.type === 'recv') return 'recv'
  if (l.type === 'error') return 'error'
  return ''
}
</script>
