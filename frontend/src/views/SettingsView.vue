<template>
  <section class="settings page">
    <h2>设置</h2>
    <div class="card-grid">
      <div class="card">
        <div class="card-head"><h3>连接</h3></div>
        <div class="field">
          <label>WS 地址</label>
          <input v-model="state.wsUrl" placeholder="ws://127.0.0.1:8765" />
        </div>
        <div class="field">
          <label>本机 ID</label>
          <input v-model="state.robotId" placeholder="controller" />
        </div>
        <div class="field">
          <label>默认 target_robot</label>
          <input v-model="state.targetRobot" placeholder="master-01" />
        </div>
        <div class="field row switch-line">
          <label>自动重连 WS</label>
          <button class="toggle-btn" :class="{on: state.autoReconnect}" @click="toggleReconnect">
            <span class="knob"></span>
          </button>
        </div>
        <button class="primary" @click="saveConfig()">保存连接配置</button>
      </div>

      <div class="card">
        <div class="card-head"><h3>自动语音回复</h3></div>
        <div class="field row switch-line">
          <label>启用自动语音回复</label>
          <button class="toggle-btn" :class="{on: state.settings.autoAiReply}" @click="toggleAi">
            <span class="knob"></span>
          </button>
        </div>
        <div class="field">
          <label>回复前缀</label>
          <input v-model="state.settings.aiPrefix" placeholder="收到：" />
        </div>
        <div class="field">
          <label>TTS 目标机器人</label>
          <input v-model="state.settings.ttsRobotId" placeholder="master-01" />
        </div>
        <div class="hint">保存后写入本地存储并下发给后端（配置会持久化到 backend/config.json）。</div>
        <button class="primary" @click="saveSettings">保存并下发</button>
      </div>

      <div class="card">
        <div class="card-head"><h3>显示</h3></div>
        <div class="field row">
          <label><input type="checkbox" v-model="autoScroll" /> 自动滚动日志/ASR</label>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../store'

const { state, saveConfig, send } = useStore()
const autoScroll = ref(true)

function toggleAi() {
  state.settings.autoAiReply = !state.settings.autoAiReply
}
function toggleReconnect() {
  state.autoReconnect = !state.autoReconnect
}

function saveSettings() {
  saveConfig()
  send({
    type: 'config_update',
    payload: {
      auto_ai_reply: state.settings.autoAiReply,
      ai_prefix: state.settings.aiPrefix,
      tts_robot_id: state.settings.ttsRobotId,
    }
  })
}
</script>

<style scoped>
.switch-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.toggle-btn {
  position: relative;
  width: 58px;
  height: 28px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.15);
  background: linear-gradient(145deg, #1a1f27, #11151c);
  cursor: pointer;
  transition: all .2s ease;
  padding: 0;
}
.toggle-btn .knob {
  position: absolute;
  top: 3px; left: 3px;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #d1d5db;
  box-shadow: 0 4px 14px rgba(0,0,0,0.3);
  transition: all .2s ease;
}
.toggle-btn.on {
  background: linear-gradient(145deg, #1ed760, #13c557);
  box-shadow: 0 6px 18px rgba(30,215,96,0.35);
}
.toggle-btn.on .knob { transform: translateX(30px); background: #fff; }
</style>
