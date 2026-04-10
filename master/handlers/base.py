from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional


@dataclass
class MasterContext:
    robot_id: str
    sim_mode: bool
    tts_service: str
    audio_topic: str
    sdk: Any
    send_tts: Callable[[str], bool]
    handle_audio_upload: Optional[Callable[[dict], Awaitable[str]]]
    execute_action: Optional[Callable[..., Awaitable[dict]]] = None
    motion_module: Any = None
    voice_module: Any = None


class MasterModule:
    name = "base"

    def __init__(self, context: MasterContext):
        self.context = context

    def capabilities(self) -> dict:
        return {}

    def status(self) -> dict:
        return {}

    async def handle(self, ws, data: dict) -> bool:
        return False
