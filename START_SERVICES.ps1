# Quick script to start both services
# Run this after setup is complete

Write-Host "Starting SCEMS services..." -ForegroundColor Cyan
Write-Host ""

# Get current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Start Supervisor in new window
Write-Host "Starting Supervisor on http://localhost:8000..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; Write-Host 'Supervisor Service' -ForegroundColor Cyan; python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Agent in new window
Write-Host "Starting Agent on http://localhost:8001..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; Write-Host 'Worker Agent Service' -ForegroundColor Cyan; python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Services started in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Wait 5-10 seconds for services to initialize, then:" -ForegroundColor Yellow
Write-Host "  1. Register agent: .\REGISTER_AGENT.ps1" -ForegroundColor White
Write-Host "  2. Test query: .\TEST_SYSTEM.ps1" -ForegroundColor White
Write-Host "  3. Or visit: http://localhost:8000/ui" -ForegroundColor White
Write-Host ""

