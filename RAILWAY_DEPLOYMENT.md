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
5. Set environment variables:
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
4. Set environment variables:
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
**Cause**: Railway passes `--port $PORT` as a literal string, and `$PORT` is not being expanded

**Solution**: The Dockerfiles now use entrypoint scripts that properly expand `$PORT`:
- `Dockerfile.supervisor` uses `/app/entrypoint_supervisor.sh`
- `Dockerfile.agent` uses `/app/entrypoint_agent.sh`

These entrypoint scripts automatically replace `$PORT` with the actual port value from the environment variable, even when Railway overrides the CMD.

**Important**: Make sure Railway is using the correct Dockerfile:
- For Supervisor: Use `Dockerfile.supervisor` or set Root Directory and Dockerfile path
- For Agent: Use `Dockerfile.agent` or set Root Directory and Dockerfile path

If Railway is still showing port errors, ensure:
1. The `PORT` environment variable is set (Railway sets this automatically)
2. The correct Dockerfile is being used
3. The entrypoint scripts are executable (they are in the Dockerfiles)

## Railway-Specific Features

The code automatically detects Railway deployment:
- Uses `RAILWAY_PUBLIC_DOMAIN` to construct agent URLs
- Reads `PORT` environment variable (Railway standard)
- Handles HTTPS URLs automatically

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

