# Quick Start Guide

## Step-by-Step Setup and Run Instructions

### 1. Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### 2. Setup Environment

```bash
# Navigate to project directory
cd scems-mas

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Sample Data

```bash
# Generate 30 days of synthetic building energy data
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
```

### 4. Train ML Model

```bash
# Train the forecasting model
python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
```

### 5. Start Services

**Terminal 1 - Supervisor:**
```bash
uvicorn supervisor.main:app --reload --port 8000
```

**Terminal 2 - Worker Agent:**
```bash
uvicorn agents.smart_campus_energy_agent.main:app --reload --port 8001
```

### 6. Register Agent

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCampusEnergyAgent",
    "base_url": "http://localhost:8001",
    "health_url": "http://localhost:8001/health",
    "capabilities": [
      "building_energy_analysis",
      "appliance_energy_breakdown",
      "peak_load_forecasting",
      "energy_saving_recommendations",
      "solar_energy_estimation",
      "cost_estimation"
    ]
  }'
```

### 7. Test the System

```bash
# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt": "Analyze energy consumption for Building A today"
  }'
```

### 8. Access Web UI

Open browser: http://localhost:8000/ui

### 9. Run Tests

```bash
# Run all tests
pytest -q

# Run specific test suite
pytest agents/smart_campus_energy_agent/tests/ -v
pytest supervisor/tests/ -v
```

### 10. Docker Deployment (Alternative)

```bash
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down
```

## Troubleshooting

### Port Already in Use
- Change ports in `shared/config.yaml` or use environment variables
- `SUPERVISOR_PORT=8002 uvicorn supervisor.main:app --port 8002`

### Import Errors
- Ensure you're in the project root directory
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Agent Not Registering
- Check that both services are running
- Verify agent health: `curl http://localhost:8001/health`
- Check supervisor registry: `curl http://localhost:8000/registry`

### LTM Errors
- Ensure write permissions in project directory
- Check LTM path in config: `shared/config.yaml`
- Try file-based LTM: Set `LTM_TYPE=file` environment variable

## Next Steps

- Read `README.md` for detailed documentation
- Check `EXAMPLE_REQUESTS.md` for API usage examples
- Review `SAMPLE_PROMPT_FOR_CURSOR.txt` for natural language query examples
- Run automated demo: `bash demo/run_demo.sh` (Linux/Mac) or `.\demo\run_demo.ps1` (Windows)

