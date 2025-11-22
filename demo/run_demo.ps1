# PowerShell version of demo script for Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SCEMS Multi-Agent System Demo" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate synthetic data
Write-Host "Step 1: Generating synthetic building energy data..." -ForegroundColor Blue
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
Write-Host "✓ Data generation complete" -ForegroundColor Green
Write-Host ""

# Step 2: Train ML model
Write-Host "Step 2: Training forecast model..." -ForegroundColor Blue
python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
Write-Host "✓ Model training complete" -ForegroundColor Green
Write-Host ""

# Step 3: Start Supervisor
Write-Host "Step 3: Starting Supervisor service..." -ForegroundColor Blue
Start-Process python -ArgumentList "-m", "uvicorn", "supervisor.main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Hidden
Start-Sleep -Seconds 3
Write-Host "✓ Supervisor started" -ForegroundColor Green
Write-Host ""

# Step 4: Start Agent
Write-Host "Step 4: Starting Worker Agent..." -ForegroundColor Blue
Start-Process python -ArgumentList "-m", "uvicorn", "agents.smart_campus_energy_agent.main:app", "--host", "0.0.0.0", "--port", "8001" -WindowStyle Hidden
Start-Sleep -Seconds 3
Write-Host "✓ Agent started" -ForegroundColor Green
Write-Host ""

# Step 5: Wait for services
Write-Host "Step 5: Waiting for services to be ready..." -ForegroundColor Blue
$maxRetries = 10
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    try {
        $supervisorHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
        $agentHealth = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($supervisorHealth.StatusCode -eq 200 -and $agentHealth.StatusCode -eq 200) {
            Write-Host "✓ Services are ready" -ForegroundColor Green
            break
        }
    } catch {
        Start-Sleep -Seconds 1
        $retryCount++
    }
}
Write-Host ""

# Step 6: Register agent
Write-Host "Step 6: Registering agent with Supervisor..." -ForegroundColor Blue
$registerBody = @{
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

Invoke-RestMethod -Uri "http://localhost:8000/register" -Method Post -Body $registerBody -ContentType "application/json" | Out-Null
Write-Host "✓ Agent registered" -ForegroundColor Green
Write-Host ""

# Step 7: Run sample queries
Write-Host "Step 7: Running sample queries..." -ForegroundColor Blue
Write-Host ""

Write-Host "Query 1: Building Energy Analysis" -ForegroundColor Yellow
$query1 = @{
    user_id = "demo_user"
    prompt = "Analyze energy consumption for Building A today"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query1 -ContentType "application/json" | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Query 2: Energy Saving Recommendations" -ForegroundColor Yellow
$query2 = @{
    user_id = "demo_user"
    prompt = "What are energy saving recommendations for Building B?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query2 -ContentType "application/json" | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "Query 3: Peak Load Forecasting" -ForegroundColor Yellow
$query3 = @{
    user_id = "demo_user"
    prompt = "Forecast peak load for Building A for the next 24 hours"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query3 -ContentType "application/json" | ConvertTo-Json -Depth 10
Write-Host ""

# Step 8: Show registry
Write-Host "Step 8: Agent Registry" -ForegroundColor Blue
Invoke-RestMethod -Uri "http://localhost:8000/registry" | ConvertTo-Json -Depth 10
Write-Host ""

# Step 9: Aggregate health
Write-Host "Step 9: Aggregate Health Status" -ForegroundColor Blue
Invoke-RestMethod -Uri "http://localhost:8000/health/aggregate" | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Demo completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Supervisor UI: http://localhost:8000/ui"
Write-Host "Supervisor API: http://localhost:8000/docs"
Write-Host "Agent API: http://localhost:8001/docs"
Write-Host ""

