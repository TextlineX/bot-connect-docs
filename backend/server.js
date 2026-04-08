// 基于 ws 的轻量 WebSocket 路由服务器
// 运行：npm install && npm start
// 环境变量：
//   WS_HOST (默认 0.0.0.0)
//   WS_PORT (默认 8765)
//   AUTH_TOKEN (可选，开启后客户端 hello 必须携带 token)
// 生产建议：前置 NGINX/Caddy 做 TLS 反代；或直接用 Cloudflare Tunnel。

require('dotenv').config();
const WebSocket = require('ws');

const HOST = process.env.WS_HOST || '0.0.0.0';
const PORT = Number(process.env.WS_PORT || 8765);
const AUTH_TOKEN = process.env.AUTH_TOKEN || '';
const PING_INTERVAL = 20000; // ms

// robot_id -> ws
const clients = new Map();

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
