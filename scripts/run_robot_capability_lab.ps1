param(
  [string]$RobotHost = "agi@192.168.88.88",
  [string]$RemoteBase = "/agibot/data/home/agi/bot_connect",
  [string]$PythonBin = "python",
  [string]$RemotePythonBin = "python3",
  [switch]$SamplePayload,
  [switch]$Phase2,
  [switch]$AllPhases,
  [switch]$AllowSideEffects
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { throw "Cannot determine script directory" }

$root = Split-Path -Parent $scriptDir
$labDir = Join-Path $root "robot_capability_lab"
$remoteLabDir = (($RemoteBase.TrimEnd('/')) + "/robot_capability_lab")
$runPhase1 = $true
$runPhase2 = $false

if ($AllPhases) {
  $runPhase1 = $true
  $runPhase2 = $true
} elseif ($Phase2) {
  $runPhase1 = $false
  $runPhase2 = $true
}

if ((-not $runPhase1) -and (-not $runPhase2)) {
  throw "At least one phase must be enabled."
}

Write-Host '[lab] Generating local inventory'
& $PythonBin (Join-Path $root 'robot_capability_lab\scripts\build_inventory.py')
& $PythonBin (Join-Path $root 'robot_capability_lab\scripts\generate_case_folders.py')

$bash = Get-Command bash -ErrorAction SilentlyContinue
$ssh = Get-Command ssh -ErrorAction SilentlyContinue
$scp = Get-Command scp -ErrorAction SilentlyContinue

if (-not $ssh) { throw "ssh command not found" }
if (-not $scp) { throw "scp command not found" }

Write-Host ('[lab] Syncing to robot: ' + $RobotHost)
if ($bash) {
  & bash (Join-Path $root 'scripts/sync_robot_capability_lab.sh') $RobotHost $RemoteBase
} else {
  & ssh $RobotHost ("rm -rf '{0}' && mkdir -p '{1}'" -f $remoteLabDir, $RemoteBase)
  & scp -r $labDir ("{0}:{1}/" -f $RobotHost, $RemoteBase)
}

$remoteArgs = New-Object System.Collections.Generic.List[string]
if ($runPhase1) { $remoteArgs.Add("--phase1") }
if ($runPhase2) { $remoteArgs.Add("--phase2") }
if ($SamplePayload) {
  $remoteArgs.Add("--sample-payload")
}
if ($AllowSideEffects) {
  $remoteArgs.Add("--allow-side-effects")
}

$remoteCmd = ("cd '{0}' && PYTHON_BIN='{1}' bash robot_capability_lab/scripts/run_probe_remote.sh" -f $RemoteBase, $RemotePythonBin)
if ($remoteArgs.Count -gt 0) {
  $remoteCmd += ' ' + ($remoteArgs -join ' ')
}

Write-Host '[lab] Running remote probes'
& ssh $RobotHost $remoteCmd

Write-Host '[lab] Pulling result files'
if ($runPhase1) {
  & scp ("{0}:{1}/inventory/generated/runtime_snapshot.json" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'inventory\generated\runtime_snapshot.json')
  & scp ("{0}:{1}/inventory/generated/runtime_summary.md" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'inventory\generated\runtime_summary.md')
}
if ($runPhase2) {
  & scp ("{0}:{1}/inventory/generated/phase2_snapshot.json" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'inventory\generated\phase2_snapshot.json')
  & scp ("{0}:{1}/inventory/generated/phase2_summary.md" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'inventory\generated\phase2_summary.md')
}
& scp -r ("{0}:{1}/cases/topics" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'cases')
& scp -r ("{0}:{1}/cases/services" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'cases')
& scp -r ("{0}:{1}/cases/actions" -f $RobotHost, $remoteLabDir) (Join-Path $labDir 'cases')

Write-Host '[lab] Done'
if ($runPhase1) {
  Write-Host ('  Phase1 summary: ' + (Join-Path $labDir 'inventory\generated\runtime_summary.md'))
  Write-Host ('  Phase1 snapshot: ' + (Join-Path $labDir 'inventory\generated\runtime_snapshot.json'))
}
if ($runPhase2) {
  Write-Host ('  Phase2 summary: ' + (Join-Path $labDir 'inventory\generated\phase2_summary.md'))
  Write-Host ('  Phase2 snapshot: ' + (Join-Path $labDir 'inventory\generated\phase2_snapshot.json'))
}
