# Register the agent with Supervisor

Write-Host "Registering SmartCampusEnergyAgent..." -ForegroundColor Cyan

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
    Write-Host "  Status: $($response.status)" -ForegroundColor Gray
    Write-Host "  Agent: $($response.agent)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Registration failed!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure Supervisor is running on http://localhost:8000" -ForegroundColor Yellow
}

