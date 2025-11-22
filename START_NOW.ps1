# Quick Start Script - Start Everything Now!
# Run this script to start both services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting SCEMS Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (-not (Test-Path .venv)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first: .\setup_and_run.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
& .venv\Scripts\Activate.ps1

# Check if services are already running
Write-Host "Checking if services are already running..." -ForegroundColor Blue
$supervisorRunning = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
$agentRunning = Test-NetConnection -ComputerName localhost -Port 8001 -InformationLevel Quiet -WarningAction SilentlyContinue

if ($supervisorRunning) {
    Write-Host "⚠ Supervisor is already running on port 8000" -ForegroundColor Yellow
} else {
    Write-Host "Starting Supervisor on http://localhost:8000..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; Write-Host '=== SUPERVISOR SERVICE ===' -ForegroundColor Cyan; Write-Host 'Running on http://localhost:8000' -ForegroundColor Green; Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow; Write-Host ''; python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000"
}

if ($agentRunning) {
    Write-Host "⚠ Agent is already running on port 8001" -ForegroundColor Yellow
} else {
    Write-Host "Starting Agent on http://localhost:8001..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; Write-Host '=== WORKER AGENT SERVICE ===' -ForegroundColor Cyan; Write-Host 'Running on http://localhost:8001' -ForegroundColor Green; Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow; Write-Host ''; python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001"
}

Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Blue
Start-Sleep -Seconds 8

# Check if services are now running
Write-Host "Checking service status..." -ForegroundColor Blue
$supervisorReady = $false
$agentReady = $false

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $supervisorReady = $true
        Write-Host "✓ Supervisor is ready!" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Supervisor not responding yet" -ForegroundColor Red
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $agentReady = $true
        Write-Host "✓ Agent is ready!" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Agent not responding yet" -ForegroundColor Red
}

Write-Host ""

if ($supervisorReady -and $agentReady) {
    # Register agent
    Write-Host "Registering agent..." -ForegroundColor Blue
    $body = @{
        name = "SmartCampusEnergyAgent"
        base_url = "http://localhost:8001"
        health_url = "http://localhost:8001/health"
        capabilities = @(
            "building_energy_analysis",
            "appliance_energy_breakdown",
            "peak_load_forecasting",
            "energy_saving_recommendations",
            "solar_energy_estimation",
            "cost_estimation"
        )
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/register" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
        Write-Host "✓ Agent registered successfully!" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Registration failed (you can register manually later)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "SUCCESS! Services are running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access your system:" -ForegroundColor White
    Write-Host "  🌐 Web UI:        http://localhost:8000/ui" -ForegroundColor Yellow
    Write-Host "  📚 Supervisor API: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host "  📚 Agent API:     http://localhost:8001/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Services are running in separate PowerShell windows." -ForegroundColor Gray
    Write-Host "Close those windows to stop the services." -ForegroundColor Gray
    Write-Host ""
    
    # Open browser
    Write-Host "Opening Web UI in browser..." -ForegroundColor Blue
    Start-Process "http://localhost:8000/ui"
    
} else {
    Write-Host "⚠ Services are starting but may need more time." -ForegroundColor Yellow
    Write-Host "Please wait 10-15 seconds, then:" -ForegroundColor Yellow
    Write-Host "  1. Open http://localhost:8000/ui in your browser" -ForegroundColor White
    Write-Host "  2. Or run: .\REGISTER_AGENT.ps1" -ForegroundColor White
    Write-Host ""
}

