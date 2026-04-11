#!/usr/bin/env python3
# 从机示例：支持 config_sync 持久化，cmd_vel / TTS 执行并回传 result
import math
import os
import sys
import time
import signal
import subprocess
import shutil
import atexit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
if COMMON.as_posix() not in sys.path:
    sys.path.insert(0, COMMON.as_posix())

from ws_client import WsClient
from role_config import save_role_config
from runtime import build_runtime
from stream_info import build_stream_urls
from action_presets import canonical_action, resolve_preset

ROLE_STATE, config_provider, on_config_sync = build_runtime(
    "slave",
    {
        "robot_id": "slave-01",
        "config_version": 0,
        "routing": {
            "brain_robot_id": "master-01",
            "control_robot_id": "slave-01",
        },
    },
)

WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")
ROBOT_ID = os.getenv("ROBOT_ID", str(ROLE_STATE.get("robot_id") or "slave-01"))
ROLE_STATE["robot_id"] = ROBOT_ID
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
SIM_MODE = os.getenv("SIM_MODE", "1") == "1"
START_TS = time.time()
MEDIAMTX_PROC = None
RELAY_PROC = None
MJPEG_PROCS: list[subprocess.Popen] = []
STREAM_MODE = os.getenv("STREAM_MODE", "rtsp").lower()  # rtsp | http_mjpeg
STREAM_PRESETS: list[dict] = []

try:
    import rclpy  # type: ignore
    from geometry_msgs.msg import Twist  # type: ignore

    RCLPY_READY = True
except Exception:
    RCLPY_READY = False

try:
    from tts_client import send_tts as ros_send_tts  # type: ignore
except Exception:
    ros_send_tts = None

try:
    from preset_motion_client import run_preset as ros_run_preset  # type: ignore
except Exception:
    ros_run_preset = None


def stop_stream_stack():
    global MEDIAMTX_PROC, RELAY_PROC, MJPEG_PROCS
    procs = [RELAY_PROC, MEDIAMTX_PROC] + MJPEG_PROCS
    for proc in procs:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass
    for proc in procs:
        if proc and proc.poll() is None:
            try:
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    MEDIAMTX_PROC = None
    RELAY_PROC = None
    MJPEG_PROCS = []


def start_stream_stack():
    """自动拉起推流栈，默认开启，缺依赖会自动跳过。"""
    global MEDIAMTX_PROC, RELAY_PROC, MJPEG_PROCS, STREAM_PRESETS
    if os.getenv("STREAM_AUTOSTART", "1").lower() not in {"1", "true", "yes"}:
        return

    if STREAM_MODE == "http_mjpeg":
        host = os.getenv("STREAM_PUBLIC_HOST") or build_stream_urls(default_name=ROBOT_ID).get("host") or "127.0.0.1"
        base_port = int(os.getenv("STREAM_HTTP_BASE", "8000"))
        topics_env = os.getenv("STREAM_TOPICS")
        topics = [t for t in (topics_env.split(",") if topics_env else []) if t.strip()]
        if not topics:
            topics = [
                "/aima/hal/sensor/rgb_head_rear/rgb_image/compressed",
                "/aima/hal/sensor/stereo_head_front_left/rgb_image/compressed",
                "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed",
                "/aima/hal/sensor/rgbd_head_front/rgb_image/compressed",
            ]
        STREAM_PRESETS = []
        port = base_port
        for topic in topics:
            cmd = [
                sys.executable,
                str(ROOT / "scripts" / "mjpeg_http_server.py"),
                "--topic",
                topic,
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
            ]
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                MJPEG_PROCS.append(proc)
                url = f"http://{host}:{port}/stream.mjpg"
                STREAM_PRESETS.append({"topic": topic, "url": url, "label": topic.split("/")[-2] if "/" in topic else topic})
                print(f"[STREAM] mjpeg started: {topic} -> {url}")
            except Exception as exc:
                print(f"[STREAM] mjpeg start failed ({topic}): {exc}")
            port += 1
        return

    mediamtx_bin = os.getenv("MEDIAMTX_BIN", "mediamtx")
    ffmpeg_bin = os.getenv("FFMPEG_BIN", "ffmpeg")
    stream = build_stream_urls(default_name=ROBOT_ID)
    rtsp_url = stream.get("rtsp_url") or f"rtsp://127.0.0.1:8554/{ROBOT_ID}"
    topic = os.getenv("STREAM_TOPIC", "/aima/hal/sensor/stereo_head_front_right/rgb_image/compressed")
    qos_rel = os.getenv("STREAM_QOS_RELIABILITY", "best_effort")
    qos_dur = os.getenv("STREAM_QOS_DURABILITY", "volatile")
    qos_depth = os.getenv("STREAM_QOS_DEPTH", "5")
    input_format = os.getenv("STREAM_INPUT_FORMAT", "mjpeg")

    mediamtx_path = shutil.which(mediamtx_bin)
    if mediamtx_path and MEDIAMTX_PROC is None:
        try:
            MEDIAMTX_PROC = subprocess.Popen(
                [mediamtx_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[STREAM] mediamtx started: {mediamtx_path}")
        except Exception as exc:
            print(f"[STREAM] mediamtx start failed: {exc}")

    relay_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "camera_rtsp_relay.py"),
        "--ros-args",
        "-p",
        f"topic:={topic}",
        "-p",
        f"rtsp_url:={rtsp_url}",
        "-p",
        f"ffmpeg_bin:={ffmpeg_bin}",
        "-p",
        f"input_format:={input_format}",
        "-p",
        f"qos_reliability:={qos_rel}",
        "-p",
        f"qos_durability:={qos_dur}",
        "-p",
        f"qos_depth:={qos_depth}",
    ]
    if RELAY_PROC is None:
        try:
            RELAY_PROC = subprocess.Popen(
                relay_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[STREAM] relay started: {topic} -> {rtsp_url}")
        except Exception as exc:
            print(f"[STREAM] relay start failed: {exc}")


def register_cleanup():
    atexit.register(stop_stream_stack)
    signal.signal(signal.SIGTERM, lambda *_: (stop_stream_stack(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda *_: (stop_stream_stack(), sys.exit(0)))


class RobotSDK:
    def __init__(self):
        self.last_velocity = {"linear": 0.0, "angular": 0.0, "at": None}
        self.node = None
        self.cmd_pub = None
        if RCLPY_READY and not SIM_MODE:
            try:
                rclpy.init(args=None)
                from rclpy.node import Node  # type: ignore

                class _Node(Node):
                    pass

                self.node = _Node("slave_cmd_bridge")
                self.cmd_pub = self.node.create_publisher(Twist, "/cmd_vel", 10)
                print("[SLAVE SDK] ROS cmd_vel publisher ready")
            except Exception as exc:
                print(f"[SLAVE SDK] ROS init failed: {exc}")
                self.node = None
                self.cmd_pub = None

    def set_velocity(self, linear: float, angular: float):
        self.last_velocity = {"linear": float(linear), "angular": float(angular), "at": time.time()}
        if self.cmd_pub:
            try:
                msg = Twist()
                msg.linear.x = float(linear)
                msg.angular.z = float(angular)
                self.cmd_pub.publish(msg)
                print(f"[SLAVE SDK] publish cmd_vel linear={linear} angular={angular}")
            except Exception as exc:
                print(f"[SLAVE SDK] publish cmd_vel failed: {exc}")
        else:
            print(f"[SLAVE SDK] set_velocity (sim) linear={linear} angular={angular}")

    def status(self):
        now = time.time()
        elapsed = now - START_TS
        last_move_at = self.last_velocity.get("at")
        battery_ratio = round(0.8 - min(elapsed / 36000, 0.15), 2)
        streams = build_stream_urls(default_name=ROBOT_ID)
        if STREAM_PRESETS:
            streams["presets"] = STREAM_PRESETS
            if not streams.get("auto_url") and len(STREAM_PRESETS) > 0:
                streams["auto_url"] = STREAM_PRESETS[0].get("url")
        if STREAM_MODE == "http_mjpeg":
            streams["preferred_player"] = "mjpg"
        return {
            "ts": now,
            "battery": battery_ratio,
            "system": {
                "hostname": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "slave-local",
                "ws_url": WS_URL,
                "sim_mode": SIM_MODE,
                "local_test": True,
                "runtime_label": "本地模拟从机",
                "uptime_sec": round(elapsed, 1),
            },
            "motion": {
                "linear": self.last_velocity.get("linear", 0.0),
                "angular": self.last_velocity.get("angular", 0.0),
                "last_command_age_sec": round(now - last_move_at, 1) if last_move_at else None,
            },
            "audio": {
                "tts_ready": bool(ros_send_tts),
                "asr_bridge_ready": False,
            },
            "sensors": {
                "battery_pct": int(battery_ratio * 100),
                "network_pct": 96,
                "audio_level_pct": int(24 + 10 * math.sin(elapsed / 4.2)),
                "imu_yaw_deg": round((elapsed * 9) % 360, 1),
                "lidar_distance_m": round(1.8 + 0.35 * math.sin(elapsed / 5.0), 2),
                "motor_temp_c": round(34 + 2.5 * math.sin(elapsed / 8.0), 1),
                "posture": "tracking",
            },
            "streams": streams,
        }


sdk = RobotSDK()


def on_cmd(data):
    payload = data.get("payload", {})
    sdk.set_velocity(payload.get("linear", 0), payload.get("angular", 0))
    return {
        "ok": True,
        "detail": "cmd_vel handled",
        "module": "slave",
        "action": "cmd_vel",
        "payload": payload,
    }


def _do_tts(text: str) -> dict:
    if ros_send_tts:
        try:
            ok = bool(ros_send_tts(text))
            return {"ok": ok, "detail": "tts ok" if ok else "tts failed"}
        except Exception as exc:
            return {"ok": False, "detail": f"tts error: {exc}"}
    return {"ok": False, "detail": "tts unavailable (no rclpy/tts_client)"}


def _do_preset(name: str, motion_id=None, area_id=None, interrupt=False) -> dict:
    if ros_run_preset:
        try:
            ok = bool(ros_run_preset(name, motion_id=motion_id, area_id=area_id, interrupt=interrupt))
            return {"ok": ok, "detail": "preset ok" if ok else "preset failed"}
        except Exception as exc:
            return {"ok": False, "detail": f"preset error: {exc}"}
    return {"ok": False, "detail": "preset unavailable (no rclpy/preset_motion_client)"}


def on_exec(data):
    payload = data.get("payload", {})
    raw_action = payload.get("action") or data.get("action")
    raw_action = str(raw_action or "").strip()
    action = canonical_action(raw_action)
    if action == "voice.tts":
        text = payload.get("text") or payload.get("message") or "你好，我是从机。"
        result = _do_tts(str(text))
        result.update({"module": "slave", "action": "voice.tts", "text": text})
        return result

    if action == "motion.move":
        sdk.set_velocity(payload.get("linear", 0), payload.get("angular", 0))
        return {
            "ok": True,
            "detail": "motion move ok",
            "module": "slave",
            "action": "motion.move",
            "payload": payload,
        }

    if action == "motion.stop":
        sdk.set_velocity(0, 0)
        return {
            "ok": True,
            "detail": "motion stop ok",
            "module": "slave",
            "action": "motion.stop",
            "payload": {"linear": 0, "angular": 0},
        }

    if action == "preset.run":
        preset = resolve_preset(raw_action, payload)
        if not preset:
            print(f"[SLAVE EXEC] unsupported preset raw={raw_action} payload={payload}")
            return {
                "ok": False,
                "detail": f"unsupported preset: {raw_action}",
                "module": "slave",
                "action": "preset.run",
                "payload": payload,
            }
        res = _do_preset(
            str(preset["name"]),
            motion_id=preset["motion_id"],
            area_id=preset["area_id"],
            interrupt=preset["interrupt"],
        )
        res.update({
            "module": "slave",
            "action": "preset.run",
            "detail": f"{res.get('detail')} | {preset['label']}",
            "payload": {
                "name": preset["name"],
                "motion_id": preset["motion_id"],
                "area_id": preset["area_id"],
                "interrupt": preset["interrupt"],
                "label": preset["label"],
                "raw_action": raw_action,
            },
        })
        print(
            "[SLAVE EXEC] preset",
            f"raw={raw_action}",
            f"name={preset['name']}",
            f"motion_id={preset['motion_id']}",
            f"area_id={preset['area_id']}",
            f"interrupt={preset['interrupt']}",
            f"ok={res.get('ok')}",
        )
        return res

    print("[SLAVE EXEC] unsupported", data)
    return {
        "ok": False,
        "detail": f"unsupported action: {action}",
        "module": "slave",
        "action": action,
        "payload": payload,
    }


def status_provider():
    return {
        "role": "slave",
        "config_version": int(ROLE_STATE.get("config_version") or 0),
        **sdk.status()
    }


def main():
    register_cleanup()
    start_stream_stack()
    save_role_config("slave", ROLE_STATE)
    client = WsClient(
        ROBOT_ID,
        WS_URL,
        AUTH_TOKEN,
        on_cmd=on_cmd,
        on_exec=on_exec,
        status_provider=status_provider,
        role="slave",
        config_provider=config_provider,
        on_config_sync=on_config_sync,
        verbose=True,
    )
    import asyncio

    asyncio.run(client.run())


if __name__ == "__main__":
    main()
