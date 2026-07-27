param(
  [string]$WslDistro = "Ubuntu",
  [int]$Models = 50,
  [int]$ScanSeeds = 10,
  [int]$CandidatesPerSeed = 500,
  [int]$SelectCount = 100
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$wslRoot = (wsl -d $WslDistro wslpath -a ($root -replace '\\','/')).Trim()
$command = "cd '$wslRoot' && MODELS=$Models SCAN_SEEDS=$ScanSeeds CANDIDATES_PER_SEED=$CandidatesPerSeed SELECT_COUNT=$SelectCount bash scripts/resume_step31.sh"
Write-Host "Launching in WSL: $command"
wsl -d $WslDistro bash -lc $command
