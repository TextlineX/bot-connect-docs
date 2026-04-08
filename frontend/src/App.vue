<template>
  <div class="app-shell">
    <h1>Bot Connect 控制台</h1>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab', { active: activeTab === tab }]"
        @click="activeTab = tab"
      >{{ tab }}</button>
    </div>

    <!-- 连接 -->
    <div class="panel" v-if="activeTab === '连接'">
      <div class="row">
        <div>
          <label>WebSocket 地址</label>
          <input v-model="wsUrl" placeholder="ws://192.168.31.170:8765" />
        </div>
        <div>
          <label>本端 robot_id</label>
          <input v-model="robotId" placeholder="controller" />
        </div>
        <div>
          <label>目标机器人</label>
          <input v-model="targetRobot" placeholder="master-01" />
        </div>
      </div>
      <div class="flex" style="margin-top:12px;">
        <button @click="connect" :disabled="connected">连接</button>
        <button @click="disconnect" :disabled="!connected">断开</button>
        <span class="badge" :class="connected ? 'green':'red'">
          {{ connected ? '已连接' : '未连接' }}
        </span>
      </div>
    </div>

    <!-- 运动控制 -->
    <div class="panel" v-if="activeTab === '运动'">
      <div class="row">
        <div>
          <label>线速度</label>
          <input type="number" step="0.05" v-model.number="linear" />
        </div>
        <div>
          <label>角速度</label>
          <input type="number" step="0.05" v-model.number="angular" />
        </div>
      </div>
      <div class="flex" style="margin-top:12px;">
        <button @click="sendCmd" :disabled="!connected">发送 cmd_vel</button>
      </div>
    </div>

    <!-- TTS -->
    <div class="panel" v-if="activeTab === 'TTS'">
      <div class="row">
        <div>
          <label>TTS 文本</label>
          <input v-model="ttsText" />
        </div>
      </div>
      <div class="flex" style="margin-top:12px;">
        <button @click="sendTts" :disabled="!connected">发送 TTS</button>
      </div>
      <div class="panel inner">
        <strong>结果回执</strong>
        <div class="log slim">
          <div v-for="(r,idx) in results" :key="idx">
            {{ r.ts }} | {{ r.detail }} | ok={{ r.ok }}
          </div>
        </div>
      </div>
    </div>

    <!-- ASR -->
    <div class="panel" v-if="activeTab === 'ASR'">
      <div class="flex" style="justify-content: space-between; align-items: center;">
        <div>显示来自 WS 的 asr_text（由 PC 端 asr_ws.py 推送）</div>
        <button @click="asrTexts=[]">清空</button>
      </div>
      <div class="log">
        <div v-for="(t,idx) in asrTexts" :key="idx">{{ t }}</div>
      </div>
    </div>

    <!-- 自定义 -->
    <div class="panel" v-if="activeTab === '自定义'">
      <label>自定义 JSON</label>
      <textarea rows="5" v-model="customJson"></textarea>
      <div class="flex" style="margin-top:8px;">
        <button @click="sendCustom" :disabled="!connected">发送自定义</button>
      </div>
    </div>

    <!-- 日志 -->
    <div class="panel" v-if="activeTab === '日志'">
      <div class="flex" style="justify-content: space-between;">
        <strong>日志</strong>
        <button @click="logs=[]">清空</button>
      </div>
      <div class="log">
        <div v-for="(item,idx) in logs" :key="idx">{{ item }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const wsUrl = ref('ws://192.168.31.170:8765')
const robotId = ref('controller')
const targetRobot = ref('master-01')
const linear = ref(0.2)
const angular = ref(0.1)
const ttsText = ref('你好，我是主机。')
const customJson = ref('{\n  "type": "ping",\n  "robot_id": "controller",\n  "ts": 0\n}')
const logs = ref([])
const results = ref([])
const asrTexts = ref([])
const connected = ref(false)
const tabs = ['连接', '运动', 'TTS', 'ASR', '自定义', '日志']
const activeTab = ref('连接')
let ws = null

const log = (msg) => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift(`[${time}] ${msg}`)
  if (logs.value.length > 200) logs.value.pop()
}

const connect = () => {
  if (connected.value) return
  ws = new WebSocket(wsUrl.value)
  ws.onopen = () => {
    connected.value = true
    const hello = { type: 'hello', robot_id: robotId.value, ts: Date.now()/1000 }
    ws.send(JSON.stringify(hello))
    log('已连接，已发送 hello')
  }
  ws.onclose = (e) => { connected.value = false; log('连接关闭 ' + e.reason) }
  ws.onerror = (e) => { log('错误 ' + (e?.message || '')) }
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      if (data.type === 'result') {
        results.value.unshift({
          ts: new Date().toLocaleTimeString(),
          ok: data.ok,
          detail: data.detail ?? '',
        })
        if (results.value.length > 100) results.value.pop()
      } else if (data.type === 'asr_text') {
        asrTexts.value.unshift(`${new Date().toLocaleTimeString()} | ${data.text}`)
        if (asrTexts.value.length > 200) asrTexts.value.pop()
      } else {
        log('收到: ' + e.data)
      }
    } catch (err) {
      log('收到: ' + e.data)
    }
  }
}

const disconnect = () => {
  if (ws) ws.close()
  ws = null
  connected.value = false
}

const sendCmd = () => {
  if (!connected.value) return
  const cmd = {
    type: 'cmd_vel',
    robot_id: robotId.value,
    target_robot: targetRobot.value,
    payload: { linear: Number(linear.value), angular: Number(angular.value) },
    ts: Date.now()/1000,
  }
  ws.send(JSON.stringify(cmd))
  log('发送 cmd_vel: ' + JSON.stringify(cmd))
}

const sendTts = () => {
  if (!connected.value) return
  const msg = {
    type: 'exec',
    robot_id: robotId.value,
    target_robot: targetRobot.value,
    payload: { action: 'tts', text: ttsText.value },
    ts: Date.now() / 1000,
  }
  ws.send(JSON.stringify(msg))
  log('发送 TTS: ' + JSON.stringify(msg))
}

const sendCustom = () => {
  if (!connected.value) return
  try {
    const obj = JSON.parse(customJson.value)
    ws.send(JSON.stringify(obj))
    log('发送自定义: ' + JSON.stringify(obj))
  } catch (e) {
    log('JSON 解析失败: ' + e.message)
  }
}

</script>
