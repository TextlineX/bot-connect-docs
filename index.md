---
layout: home

hero:
  name: "Bot Connect"
  text: "机器人控制与通信平台"
  tagline: "Vue 前端 · WebSocket 通信 · 主从机器人架构"
  actions:
    - theme: brand
      text: 快速开始
      link: /project/overview
    - theme: alt
      text: 部署指南
      link: /project/pc-deploy

features:
  - title: 前后端分离
    details: Vue 3 前端控制台 + Node.js WebSocket 中转服务，浏览器或 Electron 客户端均可
    link: /project/overview
    linkText: 查看架构

  - title: 主从机器人架构
    details: Master（大脑）负责 AI/ASR/TTS，Slave（身体）负责执行运动和视频推流
    link: /project/overview
    linkText: 了解架构

  - title: 语音交互
    details: 麦克风录音 → ASR 语音识别 → AI 指令解析 → TTS 语音播报，端到端语音控制
    link: /project/monitor
    linkText: 了解 ASR/TTS

  - title: 视频推流
    details: Slave 摄像头通过 RTSP → MediaMTX 推流，支持 WebRTC / HLS / MJPEG 多协议
    link: /project/robot-deploy
    linkText: 配置视频流

  - title: 预设动作
    details: 挥手、握手、敬礼、鞠躬、跳舞等预设动作，通过 action_router 统一调度
    link: /project/actions
    linkText: 查看动作列表

  - title: Electron 客户端
    details: 可打包为桌面客户端，解决浏览器 HTTP 环境下的音频 API 限制问题
    link: /project/pc-deploy
    linkText: Electron 部署

footer:
  message: 本文档基于 AGIBOT X2 平台构建
  copyright: MIT License
---

<div class="meteor-wrap">
  <div id="meteor-scene"></div>
  <div class="meteor-btns">
    <button data-pattern="circle">圆形</button>
    <button data-pattern="S">S 型</button>
    <button data-pattern="Z">Z 型</button>
  </div>
</div>

<script>
  if (typeof window !== 'undefined') {
    import('https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js').then(({ default: anime }) => {
      const scene = document.getElementById('meteor-scene');
      const buttons = document.querySelectorAll('.meteor-btns button');
      const meteors = [];
      const COUNT = 38;
      let cx = scene.clientWidth / 2;
      let cy = scene.clientHeight / 2;
      let currentAnim = null;

      function createMeteors() {
        for (let i = 0; i < COUNT; i++) {
          const m = document.createElement('div');
          m.className = 'meteor';
          scene.appendChild(m);
          meteors.push(m);
        }
      }

      function path(pattern, t, i) {
        const r = 70 + i * 5.5;
        const speed = 0.55 + i * 0.004;
        const a = t * speed * Math.PI * 2;
        if (pattern === 'circle') return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
        if (pattern === 'S')      return { x: cx + r * Math.sin(a), y: cy + 0.65 * r * Math.sin(2 * a) };
        if (pattern === 'Z')      return { x: cx + r * Math.sign(Math.sin(a)) * Math.pow(Math.abs(Math.sin(a)), 0.45),
                                           y: cy + r * Math.sin(a * 1.25) };
        return { x: cx, y: cy };
      }

      function run(pattern) {
        currentAnim?.pause();
        currentAnim = anime({
          targets: meteors,
          duration: 6200,
          loop: true,
          easing: 'linear',
          update: anim => {
            const t = anim.progress / 100;
            meteors.forEach((m, i) => {
              const { x, y } = path(pattern, t + i / meteors.length, i);
              m.style.transform = `translate(${x}px, ${y}px) rotate(${(t * 360 + i * 9) % 360}deg)`;
            });
          },
        });
      }

      function resize() {
        cx = scene.clientWidth / 2;
        cy = scene.clientHeight / 2;
      }

      createMeteors();
      resize();
      run('circle');

      buttons.forEach(btn =>
        btn.addEventListener('click', () => run(btn.dataset.pattern))
      );
      window.addEventListener('resize', resize);
    });
  }
</script>
