import os

from .action_router import ActionRouterModule
from .audio_asr import AudioAsrModule
from .ai_assistant import AiAssistantModule
from .motion import MotionModule
from .voice import VoiceModule


MODULE_FACTORIES = {
    "voice": VoiceModule,
    "motion": MotionModule,
    "action_router": ActionRouterModule,
    "audio_asr": AudioAsrModule,
    "ai_assistant": AiAssistantModule,
}

MODULE_CATALOG = {
    "voice": {
        "implemented": True,
        "doc": "知识库/官方/5_interface/interactor/voice.md",
        "description": "TTS and voice interaction",
    },
    "motion": {
        "implemented": True,
        "doc": "知识库/官方/5_interface/control_mod/locomotion.md",
        "description": "cmd_vel locomotion bridge",
    },
    "action_router": {
        "implemented": True,
        "doc": "master/handlers/action_router.py",
        "description": "uniform action router for exec and AI-returned actions",
    },
    "audio_asr": {
        "implemented": True,
        "doc": "知识库/02_传感器硬件抽象层/语音音频.md",
        "description": "audio upload and ASR relay",
    },
    "ai_assistant": {
        "implemented": True,
        "doc": "config/master_config.json",
        "description": "AI service bridge for ASR to JSON plus TTS message",
    },
    "modeswitch": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/control_mod/modeswitch.md",
        "description": "motion mode switch",
    },
    "preset_motion": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/control_mod/preset_motion.md",
        "description": "preset motions",
    },
    "endeffector": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/control_mod/endeffector.md",
        "description": "hand and gripper control",
    },
    "joint_control": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/control_mod/joint_control.md",
        "description": "joint control",
    },
    "vision": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/perception/vision.md",
        "description": "camera and vision",
    },
    "slam": {
        "implemented": False,
        "doc": "知识库/官方/5_interface/perception/SLAM.md",
        "description": "SLAM and map related interfaces",
    },
    "sensors": {
        "implemented": False,
        "doc": "知识库/02_传感器硬件抽象层/常用话题速查.md",
        "description": "sensor topics and status",
    },
}

DEFAULT_MODULES = ("voice", "motion", "audio_asr")


def resolve_module_names(raw: str | None = None) -> list[str]:
    value = (raw or os.getenv("MASTER_MODULES", "default")).strip().lower()
    if not value or value == "default":
        return list(DEFAULT_MODULES)
    if value == "all":
        return list(MODULE_FACTORIES.keys())
    return [name.strip() for name in value.split(",") if name.strip()]


def build_modules(context, raw: str | None = None):
    names = resolve_module_names(raw)
    enabled = []
    modules = []
    for name in names:
        factory = MODULE_FACTORIES.get(name)
        if not factory:
            print(f"[master] unknown module skipped: {name}")
            continue
        modules.append(factory(context))
        enabled.append(name)
    return modules, enabled


def module_catalog() -> dict:
    return MODULE_CATALOG
