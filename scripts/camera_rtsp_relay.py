#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CompressedImage


def build_qos(reliability: str, durability: str, depth: int) -> QoSProfile:
    rel = str(reliability or "best_effort").strip().lower()
    dur = str(durability or "volatile").strip().lower()
    return QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE if rel == "reliable" else ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.TRANSIENT_LOCAL if dur == "transient_local" else DurabilityPolicy.VOLATILE,
        history=HistoryPolicy.KEEP_LAST,
        depth=max(1, int(depth or 5)),
    )


class FFmpegRtspPublisher:
    def __init__(self, logger, ffmpeg_bin: str, rtsp_url: str, fps: float, gop_sec: float, input_format: str = "mjpeg"):
        self.logger = logger
        self.ffmpeg_bin = ffmpeg_bin
        self.rtsp_url = rtsp_url
        self.fps = max(1.0, float(fps or 10.0))
        self.gop_sec = max(0.5, float(gop_sec or 2.0))
        self.input_format = (input_format or "mjpeg").lower()
        self.proc: subprocess.Popen | None = None
        self.lock = threading.Lock()
        self.last_spawn_at = 0.0

        if not shutil.which(ffmpeg_bin):
            raise FileNotFoundError(f"ffmpeg not found: {ffmpeg_bin}")

    def _stderr_worker(self, stream):
        try:
            for raw in iter(stream.readline, b""):
                line = raw.decode("utf-8", errors="ignore").strip()
                if line:
                    self.logger.warn(f"[ffmpeg] {line}")
        except Exception:
            pass

    def _spawn(self):
        gop = max(1, int(round(self.fps * self.gop_sec)))
        if self.input_format == "h264":
            cmd = [
                self.ffmpeg_bin,
                "-hide_banner",
                "-loglevel",
                "warning",
                "-fflags",
                "nobuffer",
                "-use_wallclock_as_timestamps",
                "1",
                "-f",
                "h264",
                "-i",
                "-",
                "-an",
                "-c:v",
                "copy",
                "-f",
                "rtsp",
                "-rtsp_transport",
                "tcp",
                self.rtsp_url,
            ]
        else:
            cmd = [
                self.ffmpeg_bin,
                "-hide_banner",
                "-loglevel",
                "warning",
                "-fflags",
                "nobuffer",
                "-use_wallclock_as_timestamps",
                "1",
                "-f",
                "mjpeg",
                "-r",
                str(self.fps),
                "-i",
                "-",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-tune",
                "zerolatency",
                "-pix_fmt",
                "yuv420p",
                "-profile:v",
                "baseline",
                "-g",
                str(gop),
                "-keyint_min",
                str(gop),
                "-f",
                "rtsp",
                "-rtsp_transport",
                "tcp",
                self.rtsp_url,
            ]
        self.logger.info(f"start ffmpeg -> {self.rtsp_url}")
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self.last_spawn_at = time.monotonic()
        if self.proc.stderr:
            threading.Thread(target=self._stderr_worker, args=(self.proc.stderr,), daemon=True).start()

    def ensure_running(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                return
            now = time.monotonic()
            if now - self.last_spawn_at < 1.0:
                return
            self._spawn()

    def push_jpeg(self, frame: bytes):
        if not frame:
            return
        self.ensure_running()
        with self.lock:
            if not self.proc or self.proc.poll() is not None or not self.proc.stdin:
                return
            try:
                self.proc.stdin.write(frame)
                self.proc.stdin.flush()
            except BrokenPipeError:
                self.logger.error("ffmpeg pipe broken, wait next frame to restart")
                self._terminate_locked()
            except Exception as exc:
                self.logger.error(f"ffmpeg write failed: {exc}")
                self._terminate_locked()

    def _terminate_locked(self):
        proc = self.proc
        self.proc = None
        if not proc:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def close(self):
        with self.lock:
            self._terminate_locked()


class CameraRtspRelay(Node):
    def __init__(self):
        super().__init__("camera_rtsp_relay")
        self.declare_parameter("topic", "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed")
        self.declare_parameter("rtsp_url", "rtsp://127.0.0.1:8554/slave-camera")
        self.declare_parameter("ffmpeg_bin", "ffmpeg")
        self.declare_parameter("input_fps", 10.0)
        self.declare_parameter("gop_sec", 2.0)
        self.declare_parameter("input_format", "mjpeg")  # mjpeg | h264
        self.declare_parameter("qos_reliability", "best_effort")
        self.declare_parameter("qos_durability", "volatile")
        self.declare_parameter("qos_depth", 5)

        topic = str(self.get_parameter("topic").value)
        rtsp_url = str(self.get_parameter("rtsp_url").value)
        ffmpeg_bin = str(self.get_parameter("ffmpeg_bin").value)
        input_fps = float(self.get_parameter("input_fps").value)
        gop_sec = float(self.get_parameter("gop_sec").value)
        input_format = str(self.get_parameter("input_format").value).lower()
        qos_reliability = str(self.get_parameter("qos_reliability").value)
        qos_durability = str(self.get_parameter("qos_durability").value)
        qos_depth = int(self.get_parameter("qos_depth").value)

        self.publisher = FFmpegRtspPublisher(
            self.get_logger(),
            ffmpeg_bin=ffmpeg_bin,
            rtsp_url=rtsp_url,
            fps=input_fps,
            gop_sec=gop_sec,
            input_format=input_format,
        )
        self.frames = 0
        self.last_report_at = time.monotonic()

        qos = build_qos(qos_reliability, qos_durability, qos_depth)
        self.subscription = self.create_subscription(CompressedImage, topic, self.on_frame, qos)
        self.get_logger().info(
            f"relay {topic} -> {rtsp_url} | qos={qos_reliability}/{qos_durability} depth={qos_depth}"
        )

    def on_frame(self, msg: CompressedImage):
        fmt = str(msg.format or "").lower()
        if self.publisher.input_format != "h264":
            if fmt and "jpeg" not in fmt and "jpg" not in fmt:
                self.get_logger().warn(f"skip non-jpeg compressed frame: {msg.format}")
                return

        self.publisher.push_jpeg(bytes(msg.data))
        self.frames += 1
        now = time.monotonic()
        if now - self.last_report_at >= 5.0:
            fps = self.frames / max(now - self.last_report_at, 0.001)
            self.get_logger().info(f"relay alive, recent fps≈{fps:.1f}")
            self.frames = 0
            self.last_report_at = now

    def destroy_node(self):
        self.publisher.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = CameraRtspRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
