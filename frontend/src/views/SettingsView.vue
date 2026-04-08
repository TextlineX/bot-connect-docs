<template>
  <section class="card">
    <div class="card-head">
      <h3>设置</h3>
      <span class="pill muted">偏好</span>
    </div>
    <div class="field">
      <label><input type="checkbox" v-model="state.autoReconnect" /> 自动重连 WS</label>
    </div>
    <div class="field">
      <label><input type="checkbox" v-model="autoScroll" /> 自动滚动日志/ASR</label>
    </div>
    <div class="field">
      <label>默认 target_robot</label>
      <input v-model="state.targetRobot" />
    </div>
    <div class="field">
      <label>主题</label>
      <select>
        <option>Warm</option>
        <option disabled>Dark (预留)</option>
      </select>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../store'

const { state } = useStore()
const autoScroll = ref(true)
</script>
