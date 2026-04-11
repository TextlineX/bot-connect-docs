# 监控面板说明

## 页面概览

前端 `MonitorView.vue` 提供多路视频流监控。

## 视频流地址

```
RTSP:  rtsp://<机器人IP>:8554/<robot_id>
WebRTC: http://<机器人IP>:8889/<robot_id>
HLS:   http://<机器人IP>:8888/<robot_id>/index.m3u8
```

## 配置流地址

前端 Monitor 页面可填写机器人 IP + 端口，自动拼接流地址。

## 推流依赖

- `ffmpeg`
- `mediamtx`（MediaMTX 二进制）
- ROS 摄像头话题
