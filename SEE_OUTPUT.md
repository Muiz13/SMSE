# How to See Your Output - Quick Guide

## 🚀 Services Are Starting!

I've started both services for you. Here's how to see and interact with the output:

---

## 📺 Option 1: Web UI (Easiest - Visual Interface)

**Open your web browser and go to:**
```
http://localhost:8000/ui
```

This gives you a **visual interface** where you can:
- ✅ See all registered agents
- ✅ Type queries in a text box
- ✅ See responses displayed nicely
- ✅ No command line needed!

**Try typing:**
- "Analyze energy consumption for Building A today"
- "Forecast peak load for Building A"
- "What are energy saving recommendations?"

---

## 🌐 Option 2: Interactive API Documentation

**Supervisor API Docs:**
```
http://localhost:8000/docs
```

**Agent API Docs:**
```
http://localhost:8001/docs
```

These are **interactive Swagger UIs** where you can:
- ✅ See all available endpoints
- ✅ Test endpoints directly in the browser
- ✅ See request/response examples
- ✅ Try different queries

**How to use:**
1. Click on an endpoint (e.g., `/query`)
2. Click "Try it out"
3. Enter your data
4. Click "Execute"
5. See the response below!

---

## 💻 Option 3: PowerShell Commands (See JSON Output)

### Test Query (Natural Language)
```powershell
$query = @{
    user_id = "test_user"
    prompt = "Analyze energy consumption for Building A today"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### Direct Agent Task
```powershell
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

Invoke-RestMethod -Uri "http://localhost:8001/task/sync" -Method Post -Body $task -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### Check Registry
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/registry" | ConvertTo-Json
```

### Check Health
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health/aggregate" | ConvertTo-Json
```

---

## 📊 Option 4: View Service Logs

The services are running in the background. To see their output:

**Check if services are running:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object Id, ProcessName, StartTime
```

**View service logs:**
The services log to the console. If you started them manually, you'll see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     Started server process
```

---

## 🎯 Quick Test Examples

### Example 1: Building Energy Analysis
```powershell
$query = @{user_id="user1"; prompt="Analyze energy consumption for Building A today"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

**Expected Output:**
```json
{
  "agent": "SmartCampusEnergyAgent",
  "capability": "building_energy_analysis",
  "response": {
    "status": "SUCCESS",
    "results": {
      "data": {
        "building_id": "Building-A",
        "total_consumption_kwh": 1250.5,
        "peak_hour": 14,
        ...
      },
      "explainability": [...]
    }
  }
}
```

### Example 2: Peak Load Forecasting
```powershell
$query = @{user_id="user1"; prompt="Forecast peak load for Building A for the next 24 hours"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### Example 3: Energy Saving Recommendations
```powershell
$query = @{user_id="user1"; prompt="What are energy saving recommendations for Building B?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

---

## 🔍 What You'll See in the Output

### Successful Query Response:
- **agent**: Which agent handled the request
- **capability**: Which capability was used
- **response.status**: "SUCCESS" or "FAILURE"
- **response.results.data**: The actual data/results
- **response.results.explainability**: Explanation of the results
- **response.results.ltm_hit**: Whether result came from cache

### Example Response Structure:
```json
{
  "agent": "SmartCampusEnergyAgent",
  "capability": "building_energy_analysis",
  "response": {
    "status": "SUCCESS",
    "results": {
      "data": {
        "building_id": "Building-A",
        "date": "2025-11-22",
        "total_consumption_kwh": 1250.5,
        "peak_hour": 14,
        "average_consumption_kwh": 52.1
      },
      "explainability": [
        "Analyzed 24-hour consumption data for Building-A",
        "Total consumption: 1250.5 kWh",
        "Peak consumption occurred at 14:00"
      ],
      "ltm_hit": false
    }
  },
  "timestamp": "2025-11-22T18:00:00Z"
}
```

---

## 🎨 Best Way to See Output

**For the best experience, I recommend:**

1. **Open Web UI**: http://localhost:8000/ui
   - Easiest to use
   - Visual interface
   - See results formatted nicely

2. **Open API Docs**: http://localhost:8000/docs
   - Interactive testing
   - See all available endpoints
   - Understand the API structure

3. **Use PowerShell** (for automation/testing):
   - Run the commands above
   - See JSON output
   - Integrate into scripts

---

## ⚠️ If Services Aren't Running

If you get connection errors, start the services:

**Terminal 1:**
```powershell
cd scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2:**
```powershell
cd scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001
```

Then register the agent:
```powershell
.\REGISTER_AGENT.ps1
```

---

## ✅ Quick Checklist

- [ ] Services are running (check http://localhost:8000/health)
- [ ] Agent is registered (check http://localhost:8000/registry)
- [ ] Open Web UI: http://localhost:8000/ui
- [ ] Try a query and see the output!

---

**🎉 You're all set! Open http://localhost:8000/ui in your browser to see the output!**

