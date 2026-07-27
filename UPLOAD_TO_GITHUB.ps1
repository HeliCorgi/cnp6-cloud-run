param(
  [Parameter(Mandatory=$true)]
  [string]$RepoUrl
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "CNP6 GitHub Actions版をアップロードします。" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Gitがありません。Git for Windowsをインストールします。" -ForegroundColor Yellow
  winget install --id Git.Git -e --source winget
  Write-Host "インストール後、このPowerShellを閉じて、もう一度同じコマンドを実行してください。" -ForegroundColor Yellow
  exit 2
}

git config user.name 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { git config --global user.name "CNP6 Research" }
git config user.email 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { git config --global user.email "cnp6-local@users.noreply.github.com" }

if (-not (Test-Path ".git")) { git init }
git add .
$hasCommit = git rev-parse --verify HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
  git commit -m "Add CNP6 cloud handoff and GitHub Actions runner"
} else {
  git commit -m "Update CNP6 cloud runner" 2>$null
  if ($LASTEXITCODE -ne 0) { Write-Host "変更なし。既存内容をpushします。" }
}
git branch -M main
$remote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
  git remote set-url origin $RepoUrl
} else {
  git remote add origin $RepoUrl
}

Write-Host "GitHubへpushします。ブラウザのログイン画面が出たら許可してください。" -ForegroundColor Cyan
git push -u origin main

Write-Host "完了。GitHubで Actions → CNP6 Step 31 Cloud → Run workflow を押してください。" -ForegroundColor Green
