param(
  [Parameter(Mandatory = $true)]
  [string]$RepoUrl
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Preparing CNP6 files for GitHub..." -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Git is not installed. Installing Git for Windows..." -ForegroundColor Yellow
  winget install --id Git.Git -e --source winget
  Write-Host "Close this PowerShell window, open it again, and run the same command." -ForegroundColor Yellow
  exit 2
}

$userName = git config --global user.name
if ([string]::IsNullOrWhiteSpace($userName)) {
  git config --global user.name "CNP6 Research"
}

$userEmail = git config --global user.email
if ([string]::IsNullOrWhiteSpace($userEmail)) {
  git config --global user.email "cnp6-local@users.noreply.github.com"
}

if (-not (Test-Path ".git")) {
  git init
}

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git commit -m "Add or update CNP6 GitHub Actions runner"
} else {
  Write-Host "No new file changes. Continuing with push." -ForegroundColor Yellow
}

git branch -M main

$originExists = git remote 2>$null | Select-String -SimpleMatch "origin"
if ($originExists) {
  git remote set-url origin $RepoUrl
} else {
  git remote add origin $RepoUrl
}

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -ne 0) {
  throw "git push failed. Copy the red error message and send it here."
}

Write-Host "Done. Open GitHub, then Actions > CNP6 Step 31 Cloud > Run workflow." -ForegroundColor Green
