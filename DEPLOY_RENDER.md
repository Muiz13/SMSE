# Quick Deploy to Render (No Credit Card Required)

## 🚀 Step-by-Step Deployment

### Prerequisites
- GitHub account
- Your code pushed to GitHub

### Step 1: Push to GitHub

```bash
cd scems-mas
git init
git add .
git commit -m "Initial commit - SCEMS Multi-Agent System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/scems-mas.git
git push -u origin main
```

### Step 2: Deploy Supervisor

1. Go to https://render.com
2. Sign up with GitHub (free, no credit card)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** `scems-supervisor`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn supervisor.main:app --host 0.0.0.0 --port $PORT`
6. Click "Advanced" → Add Environment Variables:
   - `PORT` = `10000`
   - `SUPERVISOR_PORT` = `10000`
   - `LTM_TYPE` = `file`
7. Click "Create Web Service"
8. Wait for deployment (5-10 minutes)
9. **Copy the URL** (e.g., `https://scems-supervisor.onrender.com`)

### Step 3: Deploy Agent

1. In Render dashboard, click "New +" → "Web Service"
2. Connect same GitHub repository
3. Configure:
   - **Name:** `scems-agent`
   - **Region:** Same as Supervisor
   - **Branch:** `main`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `PORT` = `10001`
   - `AGENT_PORT` = `10001`
   - `SUPERVISOR_URL` = `https://scems-supervisor.onrender.com` (from Step 2)
   - `LTM_TYPE` = `file`
   - `LTM_PATH` = `/app/ltm.json`
5. Click "Create Web Service"
6. Wait for deployment

### Step 4: Register Agent

After both services are deployed:

```bash
# Register agent with supervisor
curl -X POST https://scems-supervisor.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCampusEnergyAgent",
    "base_url": "https://scems-agent.onrender.com",
    "health_url": "https://scems-agent.onrender.com/health",
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

### Step 5: Access Your App

- **Supervisor UI:** `https://scems-supervisor.onrender.com/ui`
- **Supervisor API:** `https://scems-supervisor.onrender.com/docs`
- **Agent API:** `https://scems-agent.onrender.com/docs`

---

## ⚠️ Important Notes

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - 750 hours/month free

2. **Keep Services Alive:**
   - Use a free uptime monitor (e.g., UptimeRobot)
   - Ping your services every 5 minutes

3. **Environment Variables:**
   - Update `SUPERVISOR_URL` in Agent after Supervisor deploys
   - Use `file` LTM type (no database needed)

---

## 🎉 You're Done!

Your app is now live on the internet! Share the URLs with others.


