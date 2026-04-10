# 本地配置（PowerShell），Windows 启动脚本读取
# 修改后启动脚本会自动应用
$env:WS_URL = "ws://192.168.31.170:8765"
$env:MASTER_ROBOT_ID = "master-01"
# $env:SLAVE_ROBOT_ID = "slave-01"
$env:TTS_SERVICE = "/aimdk_5Fmsgs/srv/PlayTts"
$env:MASTER_MODULES = "all"
# $env:MASTER_CONFIG_PATH = "H:\Project\Bot\bot_connect\config\master_config.json"

# 如需后端模型等，也可放这里：
# $env:MODEL_PATH = "H:\models\vosk-model-small-cn-0.22"
# $env:PYTHON_BIN = "C:\Python314\python.exe"
