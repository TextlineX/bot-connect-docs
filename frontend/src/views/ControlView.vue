<template>
  <section class="grid">
    <article class="card">
      <div class="card-head">
        <h3>动作面板</h3>
        <span class="pill">预指令</span>
      </div>
      <div class="actions">
        <button class="btn dark small" v-for="a in actions" :key="a.label" @click="sendAction(a)">
          {{ a.label }}
        </button>
      </div>
      <div class="hint">可根据需要补充具体动作指令。</div>
    </article>

    <article class="card">
      <div class="card-head">
        <h3>运动控制</h3>
        <span class="pill">cmd_vel</span>
      </div>
      <div class="field duo">
        <div><label>线速度 (m/s)</label><input type="number" step="0.05" v-model.number="linear" /></div>
        <div><label>角速度 (rad/s)</label><input type="number" step="0.05" v-model.number="angular" /></div>
      </div>
      <button class="btn dark" style="width:100%;" @click="sendCmd" :disabled="!state.connected">发送 cmd_vel</button>
    </article>

    <article class="card">
      <div class="card-head">
        <h3>自定义 JSON</h3>
        <span class="pill muted">debug</span>
      </div>
      <textarea rows="6" v-model="customJson"></textarea>
      <button class="btn dark" style="margin-top:12px;width:100%;" @click="sendCustom" :disabled="!state.connected">发送</button>
    </article>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../store'

const { state, send } = useStore()

const actions = [
  { label: '前进', payload: { linear: 0.2, angular: 0 } },
  { label: '后退', payload: { linear: -0.2, angular: 0 } },
  { label: '左转', payload: { linear: 0, angular: 0.3 } },
  { label: '右转', payload: { linear: 0, angular: -0.3 } },
  { label: '跳舞', payload: { action: 'dance' } },
]

const linear = ref(0.2)
const angular = ref(0.1)
const customJson = ref('{\n  "type": "ping",\n  "robot_id": "controller",\n  "ts": 0\n}')

function sendAction(a) {
  if (!state.connected) return
  if (a.payload.linear !== undefined) {
    send({
      type: 'cmd_vel',
      robot_id: state.robotId,
      target_robot: state.targetRobot,
      payload: a.payload,
      ts: Date.now()/1000,
    })
  } else {
    send({
      type: 'exec',
      robot_id: state.robotId,
      target_robot: state.targetRobot,
      payload: { action: a.payload.action || 'custom' },
      ts: Date.now()/1000,
    })
  }
}

function sendCmd() {
  send({
    type: 'cmd_vel',
    robot_id: state.robotId,
    target_robot: state.targetRobot,
    payload: { linear: Number(linear.value), angular: Number(angular.value) },
    ts: Date.now()/1000,
  })
}

function sendCustom() {
  try {
    const obj = JSON.parse(customJson.value)
    send(obj)
  } catch (e) {
    // ignore parse error; store logs "JSON 解析失败"?
  }
}
</script>

<style scoped>
.actions { display:flex; flex-wrap:wrap; gap:10px; }
</style>
