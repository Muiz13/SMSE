# Railway 502 Error - Complete Troubleshooting Guide

## Quick Diagnosis Steps

### Step 1: Check Agent Service Logs
1. Go to Railway Dashboard → Your Agent Service → **Logs** tab
2. Look for:
   - ✅ **Success**: `INFO:     Uvicorn running on http://0.0.0.0:XXXX`
   - ❌ **Error**: Any Python traceback, import errors, or "Application startup failed"

**Common Log Errors:**
- `ModuleNotFoundError` → Missing dependency in `requirements.txt`
- `FileNotFoundError` → Missing required file (usually OK, agent handles this)
- `Port already in use` → Port conflict (shouldn't happen with Railway)
- `Application startup failed` → Check the full error message

### Step 2: Test Agent Health Endpoint Directly
```bash
curl https://scems-agent-production.up.railway.app/health
```

**Expected Response:**
```json
{"status":"up","agent":"SmartCampusEnergyAgent"}
```

**If you get:**
- `502 Bad Gateway` → Service is down/crashed (check logs)
- `Connection refused` → Service not running
- `Timeout` → Service is starting but slow (wait 30 seconds)

### Step 3: Verify Agent Registration
```bash
curl https://your-supervisor.railway.app/registry
```

**Check:**
- Agent URL should be Railway domain (not `localhost`)
- Agent should have correct capabilities listed
- If agent is missing or has wrong URL, re-register (see below)

### Step 4: Check Supervisor Logs
1. Go to Railway Dashboard → Your Supervisor Service → **Logs** tab
2. Look for error messages when routing queries:
   - `Could not connect to agent` → Network issue
   - `Agent returned error: 502` → Agent service is down
   - `Timeout` → Agent is slow to respond

## Common Causes and Fixes

### Cause 1: Agent Service Crashed on Startup

**Symptoms:**
- Agent logs show error and then nothing
- Health endpoint returns 502
- Service shows as "Deployed" but not responding

**Fix:**
1. Check Railway logs for the exact error
2. Common issues:
   - **Missing dependency**: Add to `requirements.txt` and redeploy
   - **Import error**: Check Python version compatibility
   - **File permission error**: Check Dockerfile permissions
   - **Port binding error**: Should be handled by entrypoint script

**Action:**
```bash
# Check if service is using correct Dockerfile
# In Railway: Settings → Dockerfile Path should be: Dockerfile.agent
```

### Cause 2: Agent Not Listening on Correct Port

**Symptoms:**
- Service starts but health endpoint returns 502
- Logs show "Uvicorn running" but on wrong port

**Fix:**
1. Verify `Dockerfile.agent` is being used
2. Check that entrypoint script is executable:
   ```dockerfile
   RUN chmod +x /app/entrypoint_agent.sh
   ```
3. Verify `PORT` environment variable is set (Railway sets this automatically)

**Action:**
- Redeploy the agent service
- Check logs for "Uvicorn running on http://0.0.0.0:XXXX" message

### Cause 3: Agent URL in Registry is Wrong

**Symptoms:**
- Agent is registered but with `localhost` URL
- Supervisor can't reach agent

**Fix:**
Re-register agent with correct Railway URL:

```bash
curl -X POST https://your-supervisor.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCampusEnergyAgent",
    "base_url": "https://scems-agent-production.up.railway.app",
    "health_url": "https://scems-agent-production.up.railway.app/health",
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

### Cause 4: Network Connectivity Issues

**Symptoms:**
- Both services are running
- Health endpoints work individually
- But supervisor can't reach agent

**Fix:**
1. **Same Railway Project**: Deploy both services in the same Railway project
2. **Public Domains**: Use Railway public domains (not private networking)
3. **HTTPS**: Ensure URLs use `https://` for Railway domains

**Action:**
- Verify `SUPERVISOR_URL` environment variable in agent service is correct
- Use Railway public domain URLs, not `localhost`

### Cause 5: Agent Initialization Failed

**Symptoms:**
- Agent starts but crashes when handling requests
- Logs show initialization errors

**Fix:**
The agent now has better error handling, but check:
1. **LTM initialization**: Should fallback to file-based if SQLite fails
2. **Model loading**: Should work even if model file doesn't exist
3. **Data directory**: Should be created automatically

**Action:**
- Check agent logs for initialization errors
- Verify environment variables are set correctly

## Step-by-Step Recovery

### If Agent Service is Down:

1. **Check Logs First**
   ```
   Railway Dashboard → Agent Service → Logs
   ```

2. **Restart Service**
   ```
   Railway Dashboard → Agent Service → Settings → Restart
   ```

3. **Verify Startup**
   ```bash
   # Wait 30 seconds, then test
   curl https://scems-agent-production.up.railway.app/health
   ```

4. **Re-register if Needed**
   ```bash
   # Use the registration command above
   ```

5. **Test Query**
   ```bash
   curl -X POST https://your-supervisor.railway.app/query \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test",
       "prompt": "Analyze energy consumption for Building A"
     }'
   ```

## Verification Checklist

- [ ] Agent service shows "Deployed" status in Railway
- [ ] Agent logs show "Uvicorn running on http://0.0.0.0:XXXX"
- [ ] Agent health endpoint returns `{"status":"up","agent":"SmartCampusEnergyAgent"}`
- [ ] Agent is registered in supervisor registry with correct Railway URL
- [ ] Supervisor can reach agent (no connection errors in logs)
- [ ] Both services are in the same Railway project (or using public domains)

## Still Having Issues?

1. **Check Railway Status**: https://status.railway.app
2. **Review Recent Deployments**: Check if recent changes broke something
3. **Compare with Working Setup**: Verify Dockerfile and environment variables match documentation
4. **Check Resource Limits**: Railway free tier has limits

## Quick Test Commands

```bash
# Test agent health
curl https://scems-agent-production.up.railway.app/health

# Test supervisor health
curl https://your-supervisor.railway.app/health

# Check registry
curl https://your-supervisor.railway.app/registry

# Test query
curl -X POST https://your-supervisor.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","prompt":"Analyze Building A"}'
```

