# Complete Setup Guide - Everything You Need

## 🚀 Quick Start (Recommended)

### Option 1: Automated Setup (Easiest)

Run the complete setup script:

```powershell
cd scems-mas
.\setup_and_run.ps1
```

This script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Generate sample data
5. ✅ Train ML model
6. ✅ Start both services
7. ✅ Register the agent
8. ✅ Test the system

**That's it!** The system will be fully running.

---

## 📋 Manual Setup (Step-by-Step)

If you prefer to do it manually or the automated script has issues:

### Step 1: Prerequisites
```powershell
# Check Python (should be 3.11+)
python --version
```

### Step 2: Setup Environment
```powershell
cd scems-mas

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies
```powershell
# Install core dependencies first
pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlmodel sqlalchemy httpx requests structlog pyyaml python-dateutil python-json-logger pytest pytest-asyncio pytest-cov

# Install data science libraries
pip install numpy pandas

# Install ML library (use pre-built wheels for Windows)
pip install scikit-learn --only-binary :all:
```

### Step 4: Generate Data
```powershell
# Create directories
mkdir sample_data, models -Force

# Generate sample data
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
```

### Step 5: Train Model
```powershell
python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
```

### Step 6: Start Services

**Terminal 1 - Supervisor:**
```powershell
cd scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Agent:**
```powershell
cd scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001
```

### Step 7: Register Agent
```powershell
.\REGISTER_AGENT.ps1
```

Or manually:
```powershell
$body = @{
    name = "SmartCampusEnergyAgent"
    base_url = "http://localhost:8001"
    health_url = "http://localhost:8001/health"
    capabilities = @("building_energy_analysis","appliance_energy_breakdown","peak_load_forecasting","energy_saving_recommendations","solar_energy_estimation","cost_estimation")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/register" -Method Post -Body $body -ContentType "application/json"
```

### Step 8: Test
```powershell
.\TEST_SYSTEM.ps1
```

---

## 🛠️ Helper Scripts

I've created several helper scripts to make your life easier:

### `setup_and_run.ps1`
Complete automated setup - does everything from scratch.

### `START_SERVICES.ps1`
Quick script to start both services (use after initial setup).

### `REGISTER_AGENT.ps1`
Register the agent with Supervisor.

### `TEST_SYSTEM.ps1`
Run comprehensive tests on the system.

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] Sample data generated (`sample_data/building_energy.csv` exists)
- [ ] Model trained (`models/forecast_model.pkl` exists)
- [ ] Supervisor running (http://localhost:8000/health returns `{"status":"ok"}`)
- [ ] Agent running (http://localhost:8001/health returns `{"status":"up"}`)
- [ ] Agent registered (http://localhost:8000/registry shows the agent)
- [ ] Query works (http://localhost:8000/query with a test prompt)

---

## 🌐 Access Points

Once everything is running:

- **Supervisor Web UI**: http://localhost:8000/ui
- **Supervisor API Docs**: http://localhost:8000/docs
- **Agent API Docs**: http://localhost:8001/docs
- **Supervisor Health**: http://localhost:8000/health
- **Agent Health**: http://localhost:8001/health
- **Registry**: http://localhost:8000/registry
- **Aggregate Health**: http://localhost:8000/health/aggregate

---

## 🧪 Example Queries

Try these natural language queries:

```powershell
# Building Analysis
$query = @{user_id="test"; prompt="Analyze energy consumption for Building A today"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10

# Forecasting
$query = @{user_id="test"; prompt="Forecast peak load for Building A for the next 24 hours"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10

# Recommendations
$query = @{user_id="test"; prompt="What are energy saving recommendations for Building B?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

---

## 🐛 Troubleshooting

### Issue: scikit-learn won't install
**Solution**: Use pre-built wheels
```powershell
pip install scikit-learn --only-binary :all:
```

### Issue: Port already in use
**Solution**: Change ports in `shared/config.yaml` or use environment variables:
```powershell
$env:SUPERVISOR_PORT=8002
$env:AGENT_PORT=8003
```

### Issue: Services won't start
**Solution**: 
1. Check Python version: `python --version` (needs 3.11+)
2. Verify virtual environment is activated
3. Check all dependencies installed: `pip list`
4. Look at error messages in terminal

### Issue: Import errors
**Solution**:
1. Make sure you're in `scems-mas` directory
2. Virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

### Issue: Agent not registering
**Solution**:
1. Check both services are running
2. Wait 5-10 seconds after starting services
3. Try manual registration (see Step 7 above)

---

## 📦 What Gets Created

After setup, you'll have:

```
scems-mas/
├── .venv/                          # Virtual environment
├── sample_data/
│   └── building_energy.csv        # Generated data
├── models/
│   └── forecast_model.pkl        # Trained model
├── supervisor/
│   └── registry.json             # Agent registry
└── ltm.db                         # LTM database (created on first use)
```

---

## 🎯 Quick Commands Reference

```powershell
# Setup everything
.\setup_and_run.ps1

# Start services (after setup)
.\START_SERVICES.ps1

# Register agent
.\REGISTER_AGENT.ps1

# Test system
.\TEST_SYSTEM.ps1

# Check health
curl http://localhost:8000/health
curl http://localhost:8001/health

# View registry
curl http://localhost:8000/registry

# Run tests
pytest -q
```

---

## ✨ You're All Set!

The system is now ready to use. Start exploring:

1. Visit the Web UI: http://localhost:8000/ui
2. Try different queries
3. Explore the API docs
4. Check out the code

**Happy coding!** 🚀

