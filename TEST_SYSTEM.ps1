# Test the system with sample queries

Write-Host "Testing SCEMS Multi-Agent System" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health checks
Write-Host "Test 1: Health Checks" -ForegroundColor Blue
try {
    $supervisorHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
    Write-Host "  ✓ Supervisor: $($supervisorHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Supervisor: Not responding" -ForegroundColor Red
}

try {
    $agentHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 2
    Write-Host "  ✓ Agent: $($agentHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Agent: Not responding" -ForegroundColor Red
}
Write-Host ""

# Test 2: Registry
Write-Host "Test 2: Agent Registry" -ForegroundColor Blue
try {
    $registry = Invoke-RestMethod -Uri "http://localhost:8000/registry" -TimeoutSec 2
    Write-Host "  ✓ Found $($registry.total) registered agent(s)" -ForegroundColor Green
    foreach ($agent in $registry.agents) {
        Write-Host "    - $($agent.name): $($agent.capabilities.Count) capabilities" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Registry check failed" -ForegroundColor Red
}
Write-Host ""

# Test 3: Natural Language Query
Write-Host "Test 3: Natural Language Query" -ForegroundColor Blue
$query = @{
    user_id = "test_user"
    prompt = "Analyze energy consumption for Building A today"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" -TimeoutSec 10
    Write-Host "  ✓ Query successful!" -ForegroundColor Green
    Write-Host "    Agent: $($response.agent)" -ForegroundColor Gray
    Write-Host "    Capability: $($response.capability)" -ForegroundColor Gray
    Write-Host "    Status: $($response.response.status)" -ForegroundColor Gray
    if ($response.response.results.data.total_consumption_kwh) {
        Write-Host "    Result: $($response.response.results.data.total_consumption_kwh) kWh" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Query failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Direct Agent Task
Write-Host "Test 4: Direct Agent Task" -ForegroundColor Blue
$task = @{
    sender = "SupervisorAgent_Main"
    recipient = "SmartCampusEnergyAgent"
    type = "task_assignment"
    task = @{
        name = "peak_load_forecasting"
        priority = 2
        parameters = @{
            data = @{
                building_id = "Building-A"
                forecast_hours = 24
            }
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/task/sync" -Method Post -Body $task -ContentType "application/json" -TimeoutSec 10
    Write-Host "  ✓ Task executed successfully!" -ForegroundColor Green
    Write-Host "    Status: $($response.status)" -ForegroundColor Gray
    if ($response.results.data.peak_forecast_kwh) {
        Write-Host "    Peak Forecast: $($response.results.data.peak_forecast_kwh) kWh" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Task execution failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Aggregate Health
Write-Host "Test 5: Aggregate Health Check" -ForegroundColor Blue
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health/aggregate" -TimeoutSec 5
    Write-Host "  ✓ Supervisor Status: $($health.supervisor_status)" -ForegroundColor Green
    Write-Host "    Total Agents: $($health.total_agents)" -ForegroundColor Gray
    Write-Host "    Healthy Agents: $($health.healthy_agents)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Health check failed" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the Web UI: http://localhost:8000/ui" -ForegroundColor Yellow
Write-Host ""

