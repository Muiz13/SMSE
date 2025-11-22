# Complete Setup and Run Script for SCEMS Multi-Agent System
# This script handles all setup steps and starts the services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SCEMS Multi-Agent System Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Blue
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Create virtual environment
Write-Host "Step 2: Setting up virtual environment..." -ForegroundColor Blue
if (-not (Test-Path .venv)) {
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Activate and install dependencies
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Blue
& .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet

# Install dependencies one by one to handle Windows issues
Write-Host "  Installing core dependencies..." -ForegroundColor Gray
pip install fastapi uvicorn[standard] pydantic pydantic-settings --quiet

Write-Host "  Installing data dependencies..." -ForegroundColor Gray
pip install numpy pandas --quiet

Write-Host "  Installing ML dependencies (this may take a moment)..." -ForegroundColor Gray
# Try to install scikit-learn, if it fails, use a workaround
pip install scikit-learn --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Warning: scikit-learn installation had issues, trying alternative..." -ForegroundColor Yellow
    pip install scikit-learn --only-binary :all: --quiet 2>&1 | Out-Null
}

Write-Host "  Installing remaining dependencies..." -ForegroundColor Gray
pip install sqlmodel sqlalchemy httpx requests structlog pyyaml python-dateutil python-json-logger pytest pytest-asyncio pytest-cov --quiet

Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 4: Create necessary directories
Write-Host "Step 4: Creating directories..." -ForegroundColor Blue
@("sample_data", "models", "supervisor/templates") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Step 5: Generate sample data
Write-Host "Step 5: Generating sample data..." -ForegroundColor Blue
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Sample data generated" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Data generation had issues, but continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Train ML model
Write-Host "Step 6: Training ML model..." -ForegroundColor Blue
if (Test-Path ./sample_data/building_energy.csv) {
    python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Model trained" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Model training had issues, but continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Skipping model training (no data file found)" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Start Supervisor
Write-Host "Step 7: Starting Supervisor service..." -ForegroundColor Blue
Write-Host "  Starting on http://localhost:8000" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 5
Write-Host "✓ Supervisor started" -ForegroundColor Green
Write-Host ""

# Step 8: Start Agent
Write-Host "Step 8: Starting Worker Agent..." -ForegroundColor Blue
Write-Host "  Starting on http://localhost:8001" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .venv\Scripts\Activate.ps1; python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001" -WindowStyle Normal
Start-Sleep -Seconds 5
Write-Host "✓ Agent started" -ForegroundColor Green
Write-Host ""

# Step 9: Wait for services to be ready
Write-Host "Step 9: Waiting for services to be ready..." -ForegroundColor Blue
$maxRetries = 10
$retryCount = 0
$supervisorReady = $false
$agentReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        if (-not $supervisorReady) {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $supervisorReady = $true
                Write-Host "  ✓ Supervisor is ready" -ForegroundColor Green
            }
        }
        if (-not $agentReady) {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $agentReady = $true
                Write-Host "  ✓ Agent is ready" -ForegroundColor Green
            }
        }
        if ($supervisorReady -and $agentReady) {
            break
        }
    } catch {
        # Services not ready yet
    }
    Start-Sleep -Seconds 2
    $retryCount++
}

if (-not ($supervisorReady -and $agentReady)) {
    Write-Host "⚠ Warning: Services may not be fully ready yet" -ForegroundColor Yellow
    Write-Host "  Please wait a few more seconds and check manually" -ForegroundColor Yellow
}
Write-Host ""

# Step 10: Register agent
Write-Host "Step 10: Registering agent with Supervisor..." -ForegroundColor Blue
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
    Write-Host "✓ Agent registered successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Agent registration failed, but services are running" -ForegroundColor Yellow
    Write-Host "  You can register manually later using:" -ForegroundColor Yellow
    Write-Host "  curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{...}'" -ForegroundColor Gray
}
Write-Host ""

# Step 11: Test the system
Write-Host "Step 11: Testing the system..." -ForegroundColor Blue
try {
    $query = @{
        user_id = "test_user"
        prompt = "Analyze energy consumption for Building A today"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" -TimeoutSec 10
    Write-Host "✓ Test query successful!" -ForegroundColor Green
    Write-Host "  Response from: $($response.agent)" -ForegroundColor Gray
    Write-Host "  Capability used: $($response.capability)" -ForegroundColor Gray
} catch {
    Write-Host "⚠ Test query failed (services may still be starting)" -ForegroundColor Yellow
}
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services are running in separate windows:" -ForegroundColor White
Write-Host "  • Supervisor: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • Agent:      http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access points:" -ForegroundColor White
Write-Host "  • Supervisor Web UI: http://localhost:8000/ui" -ForegroundColor Yellow
Write-Host "  • Supervisor API:    http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  • Agent API:         http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop services, close the PowerShell windows or press Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "For more information, see HOW_TO_RUN.md" -ForegroundColor Gray
Write-Host ""

