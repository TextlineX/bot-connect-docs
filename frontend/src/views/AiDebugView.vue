<template>
  <section class="card">
    <div class="card-head">
      <h3>AI 调试</h3>
      <span class="pill">ai_result</span>
    </div>

    <div class="field duo">
      <div>
        <label>状态</label>
        <select v-model="filterOk">
          <option value="all">全部</option>
          <option value="ok">成功</option>
          <option value="fail">失败</option>
        </select>
      </div>
      <div>
        <label>来源 robot_id</label>
        <input v-model="filterSource" placeholder="controller / slave-01 ..." />
      </div>
    </div>

    <div class="field duo">
      <div>
        <label>包含 action</label>
        <select v-model="filterHasAction">
          <option value="all">全部</option>
          <option value="yes">有 action</option>
          <option value="no">无 action</option>
        </select>
      </div>
      <div>
        <label>搜索</label>
        <input v-model="filterQ" placeholder="message / intent / action / detail ..." />
      </div>
    </div>

    <div class="field duo">
      <div>
        <label>阶段</label>
        <select v-model="filterStage">
          <option value="all">全部</option>
          <option value="calling">调用中</option>
          <option value="completed">已完成</option>
          <option value="skipped">已跳过</option>
        </select>
      </div>
      <div class="hint" style="display:flex;align-items:end;">
        这里只要 ASR 文本进入 AI 模块，就会显示是否真正调用了 AI。
      </div>
    </div>

    <div class="hero-actions" style="gap:8px;">
      <button class="btn ghost small" @click="clear">清空</button>
      <span class="hint">共 {{ filtered.length }} 条</span>
    </div>

    <div class="card" style="margin-top:12px; padding:12px; border:1px dashed rgba(255,255,255,0.15);">
      <div class="card-head" style="margin-bottom:8px;">
        <h4>手动对话（不依赖 ASR）</h4>
        <span class="pill">asr_text → ai_result</span>
      </div>
      <div class="field">
        <label>目标主机 robot_id</label>
        <input v-model="manualTarget" :placeholder="state.brainTargetRobot || 'master-01'" />
      </div>
      <div class="field">
        <label>输入文本</label>
        <textarea v-model="manualText" rows="2" placeholder="直接输入要给 AI 的文字"></textarea>
      </div>
      <div class="hero-actions" style="gap:8px;">
        <button class="btn primary small" @click="sendManual" :disabled="!manualText.trim()">发送给 AI</button>
        <span class="hint">会以 asr_text 形式发送，AI 开关需开启。</span>
      </div>
    </div>

    <div class="log list" style="margin-top:12px; max-height:520px;">
      <div v-for="(item, idx) in filtered" :key="idx" class="log-card">
        <div class="meta">
          <span class="chip">{{ stageLabel(item.stage) }}</span>
          <span v-if="item.ok === true" class="chip send">ok</span>
          <span v-else-if="item.ok === false" class="chip error">fail</span>
          <span v-else class="chip">pending</span>
          <span>{{ item.ts }}</span>
          <span>robot={{ item.robot_id || '-' }}</span>
          <span>source={{ item.source_robot_id || '-' }}</span>
        </div>
        <div class="body">
          <div v-if="item.input_text" style="margin-bottom:6px;">
            <span class="chip">input</span> {{ item.input_text }}
          </div>
          <div v-if="item.data?.message" style="margin-bottom:6px;">
            <span class="chip">message</span> {{ item.data.message }}
          </div>
          <div v-if="item.data?.action" style="margin-bottom:6px;">
            <span class="chip">action</span> {{ item.data.action }}
          </div>
          <div v-if="item.skip_reason" style="margin-bottom:6px;">
            <span class="chip">skip</span> {{ item.skip_reason }}
          </div>
          <div v-if="item.detail" style="margin-bottom:6px;">
            <span class="chip">detail</span> {{ item.detail }}
          </div>
          <div v-if="item.action_result" style="margin-bottom:6px;">
            <span class="chip">action_result</span> {{ summarizeActionResult(item.action_result) }}
          </div>
          <details>
            <summary class="hint">展开 JSON</summary>
            <pre style="white-space:pre-wrap; margin:8px 0 0;">{{ pretty(item) }}</pre>
          </details>
        </div>
      </div>
      <div v-if="!filtered.length" class="hint">暂无 ai_result</div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useStore } from '../store'

const { state, send } = useStore()
const filterOk = ref('all')
const filterSource = ref('')
const filterHasAction = ref('all')
const filterQ = ref('')
const filterStage = ref('all')
const manualText = ref('')
const manualTarget = ref(state.brainTargetRobot || 'master-01')

watch(() => state.brainTargetRobot, (value) => {
  if (value && (!manualTarget.value || manualTarget.value === 'master-01')) {
    manualTarget.value = value
  }
})

function norm(s) {
  return String(s || '').trim().toLowerCase()
}

const filtered = computed(() => {
  const okMode = filterOk.value
  const src = norm(filterSource.value)
  const hasAction = filterHasAction.value
  const q = norm(filterQ.value)
  const stage = filterStage.value

  return (state.aiResults || []).filter((item) => {
    if (okMode === 'ok' && !item.ok) return false
    if (okMode === 'fail' && item.ok) return false
    if (stage !== 'all' && item.stage !== stage) return false
    if (src && !norm(item.source_robot_id).includes(src) && !norm(item.robot_id).includes(src)) return false

    const action = item?.data?.action || ''
    if (hasAction === 'yes' && !String(action).trim()) return false
    if (hasAction === 'no' && String(action).trim()) return false

    if (!q) return true
    const blob = norm(JSON.stringify(item))
  return blob.includes(q)
  })
})

function sendManual() {
  const text = manualText.value.trim()
  if (!text) return
  const now = Date.now()
  send({
    type: 'asr_text',
    robot_id: state.robotId || 'controller',
    target_robot: manualTarget.value || state.brainTargetRobot || 'master-01',
    text,
    final: true,
    session: 'manual-chat',
    seq: now,
    ts: now / 1000,
  })
  manualText.value = ''
}

function stageLabel(stage) {
  if (stage === 'calling') return '调用中'
  if (stage === 'skipped') return '已跳过'
  if (stage === 'completed') return '已完成'
  return stage || '未知'
}

function summarizeActionResult(result) {
  const action = result?.action ? `${result.action}` : '-'
  const detail = result?.detail ? `${result.detail}` : ''
  return detail ? `${action} | ${detail}` : action
}

function pretty(item) {
  try {
    return JSON.stringify(item, null, 2)
  } catch {
    return String(item)
  }
}

function clear() {
  state.aiResults = []
}
</script>
