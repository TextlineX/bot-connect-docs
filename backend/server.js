// 基于 ws 的轻量 WebSocket 路由服务器
// 运行：npm install && npm start
// 环境变量：
//   WS_HOST (默认 0.0.0.0)
//   WS_PORT (默认 8765)
//   AUTH_TOKEN (可选，开启后客户端 hello 必须携带 token)
// 生产建议：前置 NGINX/Caddy 做 TLS 反代；或直接用 Cloudflare Tunnel。

require('dotenv').config();
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

// 可选：Vosk 本地 ASR
let voskAvailable = false;
let recognizer = null;
const SAMPLE_RATE = 16000;
try {
  const vosk = require('vosk');
  const modelPath = process.env.MODEL_PATH;
  if (modelPath && fs.existsSync(modelPath)) {
    vosk.setLogLevel(0);
    const model = new vosk.Model(modelPath);
    recognizer = new vosk.Recognizer({ model, sampleRate: SAMPLE_RATE });
    voskAvailable = true;
    console.log(`[Vosk] model loaded from ${modelPath}`);
  } else {
    console.log('[Vosk] disabled: set MODEL_PATH to enable local ASR');
  }
} catch (e) {
  console.log('[Vosk] not installed (optional). npm install vosk');
}

const HOST = process.env.WS_HOST || '0.0.0.0';
const PORT = Number(process.env.WS_PORT || 8765);
const AUTH_TOKEN = process.env.AUTH_TOKEN || '';
const PING_INTERVAL = 20000; // ms

// robot_id -> ws
const clients = new Map();
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

function log(...args) { console.log(new Date().toISOString(), ...args); }

function send(ws, obj) {
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
}

function register(ws, hello) {
  const { robot_id: rid, token } = hello;
  if (!rid) throw new Error('missing robot_id');
  if (AUTH_TOKEN && token !== AUTH_TOKEN) throw new Error('invalid token');
  clients.set(rid, ws);
  ws._rid = rid;
  log(`robot ${rid} connected, online=${clients.size}`);
  send(ws, { type: 'ack', robot_id: rid });
}

function unregister(ws) {
  if (ws._rid && clients.get(ws._rid) === ws) {
    clients.delete(ws._rid);
    log(`robot ${ws._rid} disconnected, online=${clients.size}`);
  }
}

function route(fromRid, data) {
  if (data.type === 'audio_upload') {
    saveAudio(fromRid, data);
    return;
  }
  if (data.type === 'asr_text') {
    // 广播识别结果给所有客户端
    for (const [, sock] of clients.entries()) {
      send(sock, data);
    }
    return;
  }
  const target = data.target_robot;
  if (target) {
    const t = clients.get(target);
    if (t) send(t, data);
    else log(`target ${target} offline, drop ${data.type}`);
  } else {
    log(`recv ${fromRid}: ${data.type}`);
  }
}

const wss = new WebSocket.Server({ host: HOST, port: PORT });
log(`WebSocket server on ws://${HOST}:${PORT}`);

function saveAudio(fromRid, data) {
  try {
    const payload = data.payload || {};
    const b64 = payload.data;
    if (!b64) {
      log('audio_upload missing data');
      return;
    }
    const buf = Buffer.from(b64, 'base64');
    const mime = (payload.mime || '').toLowerCase();
    let ext = 'raw';
    if (mime.includes('webm')) ext = 'webm';
    else if (mime.includes('wav')) ext = 'wav';
    else if (mime.includes('ogg')) ext = 'ogg';
    const filename = `${Date.now()}_${fromRid}.${ext}`;
    const filepath = path.join(uploadDir, filename);
    fs.writeFileSync(filepath, buf);
    log(`audio_upload saved ${filename} (${buf.length} bytes)`);
    // 回发给发送方确认
    const ws = clients.get(fromRid);
    if (ws) {
      send(ws, { type: 'audio_saved', file: filename, size: buf.length, robot_id: fromRid });
    }
    // 广播给其他客户端有新音频（含原始数据，方便 ASR 直连使用）
    for (const [rid, sock] of clients.entries()) {
      if (rid !== fromRid) {
        send(sock, { ...data, saved_file: filename, ts: Date.now()/1000 });
      }
    }

    // 本地直接识别并广播 asr_text（如果 Vosk 可用）
    if (voskAvailable && recognizer) {
      try {
        recognizer.reset();
        recognizer.acceptWaveform(buf);
        const res = JSON.parse(recognizer.finalResult());
        const text = (res.text || '').trim();
        if (text) {
          log(`asr_text: ${text}`);
          for (const [, sock] of clients.entries()) {
            send(sock, { type: 'asr_text', text, robot_id: fromRid, ts: Date.now()/1000 });
          }
        }
      } catch (e) {
        log('Vosk recognize error', e.message);
      }
    }
  } catch (e) {
    log('audio_upload error', e.message);
  }
}

wss.on('connection', (ws) => {
  let alive = true;
  ws.on('pong', () => { alive = true; });

  ws.once('message', (raw) => {
    try {
      const hello = JSON.parse(raw);
      if (hello.type !== 'hello') throw new Error('first message must be hello');
      register(ws, hello);
    } catch (e) {
      log('init error', e.message);
      ws.close();
      return;
    }

    ws.on('message', (raw2) => {
      try {
        const data = JSON.parse(raw2);
        route(ws._rid, data);
      } catch (e) {
        log('msg error', e.message);
      }
    });

    ws.on('close', () => unregister(ws));
    ws.on('error', () => unregister(ws));
  });

  // 心跳保活
  const interval = setInterval(() => {
    if (!alive) {
      ws.terminate();
      clearInterval(interval);
      return;
    }
    alive = false;
    ws.ping();
  }, PING_INTERVAL);
});

process.on('SIGINT', () => { log('SIGINT, close'); wss.close(); process.exit(0); });
process.on('SIGTERM', () => { log('SIGTERM, close'); wss.close(); process.exit(0); });
