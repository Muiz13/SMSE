# Services Not Running? Here's How to Fix It

## 🚀 Quick Fix - Run This Now!

**Just run this one command:**
```powershell
cd scems-mas
.\START_NOW.ps1
```

This will:
1. ✅ Start Supervisor in a new window
2. ✅ Start Agent in a new window  
3. ✅ Register the agent
4. ✅ Open the Web UI in your browser

---

## 📋 Manual Step-by-Step (If Script Doesn't Work)

### Step 1: Open First PowerShell Window

**Open a NEW PowerShell window** and run:
```powershell
cd C:\Users\hp\Desktop\SMES\scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this window open!** This is your Supervisor service.

---

### Step 2: Open Second PowerShell Window

**Open ANOTHER NEW PowerShell window** and run:
```powershell
cd C:\Users\hp\Desktop\SMES\scems-mas
.venv\Scripts\Activate.ps1
python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

**Keep this window open too!** This is your Agent service.

---

### Step 3: Register the Agent

**Open a THIRD PowerShell window** (or use one of the above) and run:
```powershell
cd C:\Users\hp\Desktop\SMES\scems-mas
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

---

### Step 4: See Your Output!

**Open your web browser and go to:**
```
http://localhost:8000/ui
```

**OR test with PowerShell:**
```powershell
$query = @{
    user_id = "test_user"
    prompt = "Analyze energy consumption for Building A today"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $query -ContentType "application/json" | ConvertTo-Json -Depth 10
```

---

## 🔍 Troubleshooting

### Problem: "Python not found"
**Solution:**
```powershell
# Check if Python is installed
python --version

# If not found, make sure Python 3.11+ is installed
```

### Problem: "Module not found" or Import errors
**Solution:**
```powershell
cd scems-mas
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: "Port already in use"
**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Problem: "Cannot activate virtual environment"
**Solution:**
```powershell
# Recreate virtual environment
cd scems-mas
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: Services start but immediately close
**Solution:**
- Check for error messages in the window
- Make sure you're in the `scems-mas` directory
- Verify virtual environment is activated
- Check that all dependencies are installed

---

## ✅ Verify Services Are Running

**Check Supervisor:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```
Should return: `{"status":"ok"}`

**Check Agent:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
```
Should return: `{"status":"up","agent":"SmartCampusEnergyAgent"}`

**Check Registry:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/registry" | ConvertTo-Json
```
Should show your registered agent.

---

## 🎯 Quick Checklist

- [ ] Two PowerShell windows open (one for Supervisor, one for Agent)
- [ ] Both show "Uvicorn running on..."
- [ ] Both show "Application startup complete"
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:8001/health
- [ ] Agent is registered (check http://localhost:8000/registry)
- [ ] Web UI opens at http://localhost:8000/ui

---

## 💡 Pro Tip

**Use the automated script:**
```powershell
cd scems-mas
.\START_NOW.ps1
```

This does everything automatically and opens the browser for you!

---

## 📞 Still Having Issues?

1. **Check the error messages** in the PowerShell windows
2. **Verify Python version**: `python --version` (needs 3.11+)
3. **Reinstall dependencies**: `pip install -r requirements.txt`
4. **Check file paths**: Make sure you're in `scems-mas` directory
5. **Try restarting**: Close all windows and start fresh

---

**Remember:** You need **TWO PowerShell windows** running simultaneously - one for Supervisor, one for Agent!

