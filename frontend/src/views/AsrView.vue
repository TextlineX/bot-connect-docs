<template>
  <section class="card">
    <div class="card-head">
      <h3>ASR 文本流</h3>
      <div class="card-actions" style="display:flex; gap:8px; align-items:center;">
        <button class="btn ghost small" @click="paused = !paused">{{ paused ? '恢复' : '暂停' }}</button>
        <button class="btn ghost small" @click="state.asr=[]">清空</button>
      </div>
    </div>
    <div class="log">
      <div v-for="(t,idx) in viewList" :key="idx">{{ t }}</div>
      <div v-if="!state.asr.length" class="hint">暂无 ASR 文本</div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useStore } from '../store'

const { state } = useStore()
const paused = ref(false)

const viewList = computed(() => paused.value ? state.asr.slice() : state.asr)

watch(paused, v => {
  if (!v) {
    // resume scroll if needed
  }
})
</script>
