# Railway Deployment Guide

## Overview
This guide explains how to deploy the SCEMS Multi-Agent System on Railway.

## Architecture
The system consists of two services:
1. **Supervisor** - Routes queries and manages agent registry
2. **Agent** - Processes energy management tasks

## Option 1: Deploy Both Services (Recommended)

### Step 1: Deploy Supervisor Service

1. Create a new Railway project
2. Connect your GitHub repository
3. Select the repository root directory
4. **Important**: Set the Dockerfile path to `Dockerfile.supervisor`
   - In Railway service settings, go to "Settings" → "Dockerfile Path"
   - Set it to `Dockerfile.supervisor`
5. **CRITICAL**: Remove any "Start Command" override
   - In Railway service settings, go to "Settings" → "Start Command"
   - **Leave it empty** (or remove any existing command)
   - The Dockerfile CMD will be used automatically
   - If you must set a start command, use: `python -m supervisor.main`
6. Set environment variables:
   - `PORT` - Railway will set this automatically
   - `REGISTRY_PATH` - `/app/supervisor/registry.json` (default)
6. Deploy

**Note the Supervisor URL** (e.g., `https://your-supervisor.railway.app`)

### Step 2: Deploy Agent Service

1. In the same Railway project, create a **new service**
2. Use the same repository
3. **Important**: Set the Dockerfile path to `Dockerfile.agent`
   - In Railway service settings, go to "Settings" → "Dockerfile Path"
   - Set it to `Dockerfile.agent`
4. **CRITICAL**: Remove any "Start Command" override
   - In Railway service settings, go to "Settings" → "Start Command"
   - **Leave it empty** (or remove any existing command)
   - The Dockerfile CMD will be used automatically
   - If you must set a start command, use: `python -m agents.smart_campus_energy_agent.main`
5. Set environment variables:
   - `PORT` - Railway will set this automatically
   - `SUPERVISOR_URL` - Your supervisor URL from Step 1 (e.g., `https://your-supervisor.railway.app`)
   - `AGENT_BASE_URL` - Your agent's Railway URL (will be set automatically via `RAILWAY_PUBLIC_DOMAIN`)
   - `LTM_TYPE` - `file` (recommended for Railway)
   - `LTM_PATH` - `/app/ltm.json`
6. Deploy

The agent will **auto-register** with the supervisor on startup using its Railway public domain.

### Step 3: Verify Deployment

1. Visit your Supervisor URL: `https://your-supervisor.railway.app/ui`
2. Check that the agent is registered
3. Test a query from the UI

## Option 2: Deploy Supervisor Only (Manual Agent Registration)

If you only deploy the supervisor:

1. Deploy the supervisor as described in Step 1 above
2. Manually register your agent using the `/register` endpoint:

```bash
curl -X POST https://your-supervisor.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCampusEnergyAgent",
    "base_url": "https://your-agent.railway.app",
    "health_url": "https://your-agent.railway.app/health",
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

Replace `your-agent.railway.app` with your actual agent URL.

## Environment Variables Reference

### Supervisor Service
- `PORT` - Port number (Railway sets automatically)
- `REGISTRY_PATH` - Path to registry file (default: `/app/supervisor/registry.json`)
- `SUPERVISOR_PORT` - Alternative port env var (falls back to PORT)

### Agent Service
- `PORT` - Port number (Railway sets automatically)
- `AGENT_PORT` - Alternative port env var (falls back to PORT)
- `SUPERVISOR_URL` - Supervisor service URL (required)
- `AGENT_BASE_URL` - Agent's public URL (optional, auto-detected from RAILWAY_PUBLIC_DOMAIN)
- `LTM_TYPE` - `file` or `sqlite` (use `file` for Railway)
- `LTM_PATH` - Path to LTM file (e.g., `/app/ltm.json`)

## Troubleshooting

### Issue: "All connection attempts failed"
**Cause**: Agent URL in registry is incorrect (likely `localhost`)

**Solution**:
1. Check the registry at `/registry` endpoint
2. If agent URL is `localhost`, update it:
   - Deploy the agent service and let it auto-register, OR
   - Manually register with correct Railway URL using `/register` endpoint

### Issue: Agent not auto-registering
**Cause**: Supervisor URL not set or incorrect

**Solution**:
1. Verify `SUPERVISOR_URL` environment variable is set correctly
2. Check agent logs for registration errors
3. Manually register if needed

### Issue: Port errors - "Invalid value for '--port': '$PORT' is not a valid integer"
**Cause**: Railway is passing `--port $PORT` as a literal string, and `$PORT` is not being expanded

**Solution**: 
1. **Remove Start Command Override** (Most Important!)
   - Go to Railway Dashboard → Your Service → Settings → Start Command
   - **Delete any start command** (leave it empty)
   - Railway will use the Dockerfile CMD which uses the Python module (reads PORT from env)

2. **If you must use a start command**, use:
   - Supervisor: `python -m supervisor.main`
   - Agent: `python -m agents.smart_campus_energy_agent.main`
   
   **DO NOT use**: `uvicorn ... --port $PORT` (this won't work!)

3. **Verify Dockerfile is correct**:
   - Supervisor: `Dockerfile.supervisor`
   - Agent: `Dockerfile.agent`

4. **The entrypoint scripts handle PORT expansion**, but only if Railway doesn't override with a direct uvicorn command.

**Quick Fix**:
1. Remove any "Start Command" in Railway service settings
2. Redeploy the service
3. The Python module will read PORT from environment automatically

### Issue: 502 Bad Gateway Error - "Agent returned error: 502"
**Cause**: The supervisor cannot reach the agent service, or the agent service is down/crashed

**Diagnosis Steps**:

1. **Check Agent Service Status**:
   - Go to Railway dashboard → Agent service → Logs
   - Look for errors during startup
   - Verify the service is running (not crashed)

2. **Check Agent Health Endpoint**:
   ```bash
   curl https://your-agent.railway.app/health
   ```
   Should return: `{"status":"up","agent":"SmartCampusEnergyAgent"}`

3. **Verify Agent Registration**:
   ```bash
   curl https://your-supervisor.railway.app/registry
   ```
   Check that the agent URL is correct (should be Railway domain, not localhost)

4. **Check Agent Logs**:
   - Look for startup errors
   - Check if the agent is listening on the correct port
   - Verify no import errors or missing dependencies

**Common Causes and Solutions**:

1. **Agent Service Crashed**:
   - Check Railway logs for the agent service
   - Look for Python errors, import errors, or missing files
   - Ensure all dependencies are in `requirements.txt`
   - Verify model files exist if required

2. **Incorrect Agent URL in Registry**:
   - The agent may have registered with `localhost` instead of Railway domain
   - Solution: Re-register the agent with the correct Railway URL:
     ```bash
     curl -X POST https://your-supervisor.railway.app/register \
       -H "Content-Type: application/json" \
       -d '{
         "name": "SmartCampusEnergyAgent",
         "base_url": "https://your-agent.railway.app",
         "health_url": "https://your-agent.railway.app/health",
         "capabilities": ["building_energy_analysis", "appliance_energy_breakdown", "peak_load_forecasting", "energy_saving_recommendations", "solar_energy_estimation", "cost_estimation"]
       }'
     ```

3. **Agent Not Auto-Registering**:
   - Check that `SUPERVISOR_URL` environment variable is set correctly in the agent service
   - Verify the supervisor URL is accessible from the agent
   - Check agent logs for registration errors

4. **Network Connectivity Issues**:
   - If services are in different Railway projects, they may not be able to communicate
   - Solution: Deploy both services in the same Railway project, or use public domains

5. **Agent Service Not Listening on Port**:
   - Verify the agent is using the entrypoint script (should handle PORT correctly)
   - Check that the service is binding to `0.0.0.0`, not `127.0.0.1`
   - Ensure the Dockerfile is using `Dockerfile.agent`

**Quick Fix**:
1. Check agent service logs in Railway dashboard
2. Verify agent health endpoint is accessible
3. Re-register agent with correct Railway URL if needed
4. Restart both services if issues persist

## Railway-Specific Features

The code automatically detects Railway deployment:
- Uses `RAILWAY_PUBLIC_DOMAIN` to construct agent URLs
- Reads `PORT` environment variable (Railway standard)
- Handles HTTPS URLs automatically

## Quick Diagnostic Checklist for 502 Errors

**📋 For detailed troubleshooting, see [RAILWAY_502_TROUBLESHOOTING.md](./RAILWAY_502_TROUBLESHOOTING.md)**

If you're getting a 502 error, run through this checklist:

1. **Check Agent Service is Running**:
   ```bash
   # In Railway dashboard, go to Agent service → Logs
   # Look for "Uvicorn running on..." message
   # Check for any error messages
   ```

2. **Test Agent Health Endpoint**:
   ```bash
   curl https://your-agent.railway.app/health
   # Should return: {"status":"up","agent":"SmartCampusEnergyAgent"}
   ```

3. **Check Agent Registration**:
   ```bash
   curl https://your-supervisor.railway.app/registry
   # Verify agent URL is Railway domain (not localhost)
   ```

4. **Check Supervisor Logs**:
   ```bash
   # In Railway dashboard, go to Supervisor service → Logs
   # Look for connection errors or timeout messages
   ```

5. **Re-register Agent if Needed**:
   ```bash
   curl -X POST https://your-supervisor.railway.app/register \
     -H "Content-Type: application/json" \
     -d '{
       "name": "SmartCampusEnergyAgent",
       "base_url": "https://your-agent.railway.app",
       "health_url": "https://your-agent.railway.app/health",
       "capabilities": ["building_energy_analysis", "appliance_energy_breakdown", "peak_load_forecasting", "energy_saving_recommendations", "solar_energy_estimation", "cost_estimation"]
     }'
   ```

## Quick Start Commands

### Check Supervisor Health
```bash
curl https://your-supervisor.railway.app/health
```

### List Registered Agents
```bash
curl https://your-supervisor.railway.app/registry
```

### Register Agent Manually
```bash
curl -X POST https://your-supervisor.railway.app/register \
  -H "Content-Type: application/json" \
  -d @agent-registration.json
```

### Test Query
```bash
curl -X POST https://your-supervisor.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt": "Analyze energy consumption for Building A"
  }'
```

