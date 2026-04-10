# Master capability modules

The master client is now split into small modules under `master/handlers/`.
Enable modules with `MASTER_MODULES`, for example:

```bash
export MASTER_MODULES=voice,motion,audio_asr
python client.py
```

If `MASTER_MODULES` is empty or set to `default`, these modules are enabled:
- `voice`
- `motion`
- `audio_asr`

If `MASTER_MODULES=all`, all currently implemented modules are enabled.

## Implemented modules

### `voice`
- Purpose: TTS and voice interaction
- Message types:
  - `exec` with `action=tts`
- Knowledge source:
  - `知识库/官方/5_interface/interactor/voice.md`

### `motion`
- Purpose: locomotion bridge for `cmd_vel`
- Message types:
  - `cmd_vel`
- Knowledge source:
  - `知识库/官方/5_interface/control_mod/locomotion.md`

### `action_router`
- Purpose: route `exec` and AI-returned `action/params` into real module actions
- Message types:
  - `exec`
- Supports:
  - `voice.tts`
  - `motion.move`
  - `motion.stop`
  - `preset.run`
- Notes:
  - supports English and Chinese aliases such as `前进` / `停止` / `挥手` / `跳舞`
  - preset motion uses `/aimdk_5Fmsgs/srv/SetMcPresetMotion` when not in sim mode

### `audio_asr`
- Purpose: audio upload and ASR relay
- Message types:
  - `audio_upload`
- Knowledge source:
  - `知识库/02_传感器硬件抽象层/语音音频.md`

### `ai_assistant`
- Purpose: send ASR text to an AI service, require JSON output, and use `message` for TTS
- Message types:
  - `asr_text`
  - `master_config_update`
- Config:
  - `config/master_config.json`
- Notes:
  - the JSON response must contain a `message` field
  - `message` is used for TTS when `auto_tts=true`
  - if AI returns `action` plus `params`, the action router will execute it

## Planned modules

### `modeswitch`
- Purpose: motion mode switch
- Knowledge source:
  - `知识库/官方/5_interface/control_mod/modeswitch.md`

### `preset_motion`
- Purpose: preset motions
- Knowledge source:
  - `知识库/官方/5_interface/control_mod/preset_motion.md`

### `endeffector`
- Purpose: hand and gripper control
- Knowledge source:
  - `知识库/官方/5_interface/control_mod/endeffector.md`

### `joint_control`
- Purpose: joint control
- Knowledge source:
  - `知识库/官方/5_interface/control_mod/joint_control.md`

### `vision`
- Purpose: camera and vision interfaces
- Knowledge source:
  - `知识库/官方/5_interface/perception/vision.md`

### `slam`
- Purpose: SLAM and map related interfaces
- Knowledge source:
  - `知识库/官方/5_interface/perception/SLAM.md`

### `sensors`
- Purpose: sensor topics and status aggregation
- Knowledge source:
  - `知识库/02_传感器硬件抽象层/常用话题速查.md`
