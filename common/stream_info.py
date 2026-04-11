from __future__ import annotations

import os
import socket
from typing import Dict


def _flag_enabled(name: str, default: str = "1") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value not in {"0", "false", "no", "off", ""}


def _guess_ipv4() -> str:
    candidates: list[str] = []

    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM)
        for info in infos:
            ip = info[4][0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            if ip not in candidates:
                candidates.append(ip)
    except Exception:
        pass

    if candidates:
        return candidates[0]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
    except Exception:
        pass

    return ""


def _safe_port(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def build_stream_urls(default_name: str = "slave-camera") -> Dict:
    if not _flag_enabled("STREAM_ENABLE", "1"):
        return {}

    public_host = str(os.getenv("STREAM_PUBLIC_HOST") or "").strip()
    if not public_host:
        public_host = _guess_ipv4()
    if not public_host:
        return {}

    stream_name = str(os.getenv("STREAM_NAME") or default_name or "slave-camera").strip().strip("/")
    if not stream_name:
        stream_name = "slave-camera"

    rtsp_port = _safe_port("STREAM_RTSP_PORT", 8554)
    webrtc_port = _safe_port("STREAM_WEBRTC_PORT", 8889)
    hls_port = _safe_port("STREAM_HLS_PORT", 8888)
    topic = str(os.getenv("STREAM_TOPIC") or "").strip()
    mode = str(os.getenv("STREAM_MODE", "rtsp")).lower()
    http_port = _safe_port("STREAM_HTTP_PORT", 8000)

    webrtc_page_url = f"http://{public_host}:{webrtc_port}/{stream_name}"

    if mode == "http_mjpeg":
        mjpeg_url = f"http://{public_host}:{http_port}/stream.mjpg"
        return {
            "enabled": True,
            "host": public_host,
            "name": stream_name,
            "topic": topic,
            "mjpeg_url": mjpeg_url,
            "auto_url": mjpeg_url,
            "preferred_player": "mjpg",
        }

    return {
        "enabled": True,
        "host": public_host,
        "name": stream_name,
        "topic": topic,
        "rtsp_port": rtsp_port,
        "webrtc_port": webrtc_port,
        "hls_port": hls_port,
        "rtsp_url": f"rtsp://{public_host}:{rtsp_port}/{stream_name}",
        "webrtc_page_url": webrtc_page_url,
        "webrtc_whep_url": f"{webrtc_page_url}/whep",
        "hls_url": f"http://{public_host}:{hls_port}/{stream_name}/index.m3u8",
        "preferred_player": "webrtc",
    }
