# How to Run SCEMS Multi-Agent System

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11 or higher installed
- ✅ pip (Python package manager)
- ✅ Terminal/PowerShell access

Check Python version:
```bash
python --version
```

## Step-by-Step Instructions

### Step 1: Navigate to Project Directory

```bash
cd scems-mas
```

### Step 2: Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your prompt when activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages (FastAPI, uvicorn, scikit-learn, etc.).

### Step 4: Generate Sample Data

```bash
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
```

This creates synthetic building energy data for 30 days.

### Step 5: Train ML Model

```bash
# Create models directory if it doesn't exist
mkdir models

# Train the forecasting model
python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
```

### Step 6: Start Supervisor Service

**Open a new terminal/PowerShell window** and run:

```bash
cd scems-mas
.venv\Scripts\Activate.ps1  # Activate venv again
uvicorn supervisor.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Keep this terminal open!

### Step 7: Start Worker Agent

**Open another new terminal/PowerShell window** and run:

```bash
cd scems-mas
.venv\Scripts\Activate.ps1  # Activate venv again
uvicorn agents.smart_campus_energy_agent.main:app --reload --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

Keep this terminal open too!

### Step 8: Register the Agent

**Open a third terminal/PowerShell window** and run:

**Windows (PowerShell):**
```powershell
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

Invoke-RestMethod -Uri "http://localhost:8000/register" -Method Post -Body $body -ContentType "application/json"
```

**Windows (Command Prompt) or Linux/Mac:**
```bash
curl -X POST http://localhost:8000/register ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"SmartCampusEnergyAgent\",\"base_url\":\"http://localhost:8001\",\"health_url\":\"http://localhost:8001/health\",\"capabilities\":[\"building_energy_analysis\",\"appliance_energy_breakdown\",\"peak_load_forecasting\",\"energy_saving_recommendations\",\"solar_energy_estimation\",\"cost_estimation\"]}"
```

You should see a response like:
```json
{
  "status": "registered",
  "agent": "SmartCampusEnergyAgent"
}
```

### Step 9: Test the System

**Test 1: Health Check**
```bash
# Supervisor
curl http://localhost:8000/health

# Agent
curl http://localhost:8001/health
```

**Test 2: Natural Language Query**

**Windows (PowerShell):**
```powershell
$query = @{
    user_id = "test_user"
    prompt = "Analyze energy consumption for Building A today"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

**Windows (Command Prompt) or Linux/Mac:**
```bash
curl -X POST http://localhost:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"test_user\",\"prompt\":\"Analyze energy consumption for Building A today\"}"
```

**Test 3: Direct Agent Task**

**Windows (PowerShell):**
```powershell
$task = @{
    sender = "SupervisorAgent_Main"
    recipient = "SmartCampusEnergyAgent"
    type = "task_assignment"
    task = @{
        name = "building_energy_analysis"
        priority = 2
        parameters = @{
            data = @{
                building_id = "Building-A"
                date = "today"
            }
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8001/task/sync" -Method Post -Body $task -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### Step 10: Access Web UI

Open your browser and navigate to:
```
http://localhost:8000/ui
```

This provides a simple web interface to:
- View registered agents
- Send queries to agents
- See responses

### Step 11: View API Documentation

- **Supervisor API Docs**: http://localhost:8000/docs
- **Agent API Docs**: http://localhost:8001/docs

These are interactive Swagger/OpenAPI documentation pages.

## Quick Test Commands

### Check Registry
```bash
curl http://localhost:8000/registry
```

### Get Agent Capabilities
```bash
curl http://localhost:8001/capabilities
```

### Aggregate Health Check
```bash
curl http://localhost:8000/health/aggregate
```

## Example Queries

Try these natural language queries via the `/query` endpoint:

1. **Building Analysis:**
   ```
   "Analyze energy consumption for Building A today"
   ```

2. **Appliance Breakdown:**
   ```
   "Show me the energy breakdown by appliance for Building B"
   ```

3. **Forecasting:**
   ```
   "Forecast peak load for Building A for the next 24 hours"
   ```

4. **Recommendations:**
   ```
   "What are energy saving recommendations for Building C?"
   ```

5. **Solar Estimation:**
   ```
   "Estimate solar energy generation for 100kW panels"
   ```

6. **Cost Analysis:**
   ```
   "What is the cost for 1000 kWh consumption at $0.12 per kWh?"
   ```

## Troubleshooting

### Port Already in Use

If port 8000 or 8001 is already in use:

**Option 1: Change ports in config**
Edit `shared/config.yaml` and change the port numbers.

**Option 2: Use environment variables**
```bash
# Terminal 1 (Supervisor)
$env:SUPERVISOR_PORT=8002
uvicorn supervisor.main:app --port 8002

# Terminal 2 (Agent)
$env:AGENT_PORT=8003
uvicorn agents.smart_campus_energy_agent.main:app --port 8003
```

### Import Errors

If you see import errors:
1. Make sure you're in the `scems-mas` directory
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

### Agent Not Registering

1. Check both services are running:
   - Supervisor: http://localhost:8000/health
   - Agent: http://localhost:8001/health

2. Check agent health:
   ```bash
   curl http://localhost:8001/health
   ```

3. Try manual registration again (Step 8)

### Services Won't Start

1. Check Python version: `python --version` (should be 3.11+)
2. Check all dependencies installed: `pip list`
3. Check for error messages in terminal output

## Running Tests

```bash
# Run all tests
pytest -q

# Run specific test suite
pytest agents/smart_campus_energy_agent/tests/ -v
pytest supervisor/tests/ -v
```

## Using Docker (Alternative)

If you prefer Docker:

```bash
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down
```

This starts both Supervisor and Agent automatically.

## Automated Demo Script

For a complete automated demo:

**Windows:**
```powershell
.\demo\run_demo.ps1
```

**Linux/Mac:**
```bash
bash demo/run_demo.sh
```

This script will:
1. Generate data
2. Train model
3. Start services
4. Register agent
5. Run sample queries
6. Show results

## Next Steps

- Read `README.md` for detailed documentation
- Check `EXAMPLE_REQUESTS.md` for more API examples
- Review `SAMPLE_PROMPT_FOR_CURSOR.txt` for query examples
- Explore the code in `supervisor/` and `agents/` directories

## Stopping the Services

To stop the services:
1. Go to each terminal window running uvicorn
2. Press `Ctrl+C` to stop each service
3. Deactivate virtual environment: `deactivate`

---

**You're all set!** The system should now be running and ready to process queries. 🚀

