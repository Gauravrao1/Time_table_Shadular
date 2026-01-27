param(
  [string]$BackendPort = "8000",
  [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Smart Timetable Scheduler..." -ForegroundColor Cyan

# Backend setup and run
Push-Location backend
if (!(Test-Path .venv)) {
  Write-Host "Creating Python venv..." -ForegroundColor Yellow
  python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null

$backendCmd = "uvicorn app.main:app --host 0.0.0.0 --port $BackendPort --reload"
Write-Host "Launching backend: $backendCmd" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit","-Command",$backendCmd -WorkingDirectory (Get-Location)
Pop-Location

# Frontend serve
Push-Location frontend
$frontendCmd = "python -m http.server $FrontendPort"
Write-Host "Serving frontend: $frontendCmd" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit","-Command",$frontendCmd -WorkingDirectory (Get-Location)
Pop-Location

Write-Host "Open frontend at http://127.0.0.1:$FrontendPort" -ForegroundColor Cyan
Write-Host "Set Backend API URL to http://127.0.0.1:$BackendPort and click Test Connection" -ForegroundColor Cyan
