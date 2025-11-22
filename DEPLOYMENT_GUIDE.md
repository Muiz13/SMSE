# Deployment Guide - Free Platforms (No Credit Card Required)

## 🚀 Recommended Free Deployment Platforms

### Option 1: **Render** (Recommended - Easiest)
**Free Tier:** ✅ Yes | **Credit Card:** ❌ Not Required for Free Tier

**Pros:**
- Easy deployment from GitHub
- Free PostgreSQL/Redis available
- Automatic HTTPS
- Good documentation

**Limitations:**
- Free tier spins down after 15 minutes of inactivity
- 750 hours/month free

**Deployment Steps:**
1. Push your code to GitHub
2. Go to https://render.com
3. Sign up with GitHub
4. Click "New +" → "Web Service"
5. Connect your GitHub repo
6. Settings:
   - **Name:** scems-supervisor
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn supervisor.main:app --host 0.0.0.0 --port $PORT`
   - **Port:** Auto-detected
7. Add environment variables:
   - `SUPERVISOR_PORT=10000`
   - `AGENT_PORT=10001`
8. Repeat for Agent service (separate web service)

---

### Option 2: **Koyeb** (Best for Multiple Services)
**Free Tier:** ✅ Yes | **Credit Card:** ❌ Not Required

**Pros:**
- No credit card needed
- Free tier doesn't sleep
- Easy Docker deployment
- Multiple services support

**Limitations:**
- 2 services free
- 512MB RAM per service

**Deployment Steps:**
1. Push code to GitHub
2. Go to https://www.koyeb.com
3. Sign up with GitHub
4. Create new App → "Docker"
5. Connect GitHub repo
6. Dockerfile path: `Dockerfile`
7. Port: 8000 (for Supervisor)
8. Repeat for Agent (separate app, port 8001)

---

### Option 3: **PythonAnywhere** (Simple Python Hosting)
**Free Tier:** ✅ Yes | **Credit Card:** ❌ Not Required

**Pros:**
- Designed for Python apps
- Simple deployment
- Free MySQL database

**Limitations:**
- Only 1 web app on free tier
- Limited to PythonAnywhere subdomain
- Manual setup required

**Deployment Steps:**
1. Go to https://www.pythonanywhere.com
2. Sign up for free account
3. Upload your code via Files tab
4. Open Bash console
5. Install dependencies: `pip3.10 install --user -r requirements.txt`
6. Create web app:
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Flask (we'll modify it)
   - Set source code path
   - Modify WSGI file to use uvicorn

---

### Option 4: **Replit** (Development + Deployment)
**Free Tier:** ✅ Yes | **Credit Card:** ❌ Not Required

**Pros:**
- Full IDE in browser
- Easy to deploy
- Can run multiple services

**Limitations:**
- Free tier has resource limits
- May sleep after inactivity

**Deployment Steps:**
1. Go to https://replit.com
2. Sign up with GitHub
3. Import your GitHub repo
4. Install dependencies in shell
5. Use "Run" button or configure as web app
6. Deploy as web app from sidebar

---

### Option 5: **Cyclic** (Serverless)
**Free Tier:** ✅ Yes | **Credit Card:** ❌ Not Required

**Pros:**
- Serverless deployment
- Auto-scaling
- Free tier available

**Limitations:**
- Better for single service apps
- May need to combine services

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Code is pushed to GitHub/GitLab
- [ ] All dependencies in `requirements.txt`
- [ ] Environment variables documented
- [ ] Database/Redis optional (can use file-based LTM)
- [ ] Port configuration uses environment variables

---

## 🔧 Platform-Specific Configurations

### For Render/Koyeb (Docker-based)

Create separate Dockerfiles or use docker-compose:

**Dockerfile.supervisor:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "supervisor.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile.agent:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "agents.smart_campus_energy_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Environment Variables Needed

```bash
# Supervisor
SUPERVISOR_PORT=8000
SUPERVISOR_HOST=0.0.0.0
REGISTRY_PATH=/app/supervisor/registry.json

# Agent
AGENT_PORT=8001
AGENT_HOST=0.0.0.0
SUPERVISOR_URL=https://your-supervisor-url.onrender.com
LTM_TYPE=file
LTM_PATH=/app/ltm.json
```

---

## 🎯 Recommended Approach: Render (Easiest)

### Step-by-Step for Render:

1. **Prepare your code:**
   ```bash
   # Make sure everything is committed
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy Supervisor:**
   - Go to https://render.com
   - Sign up with GitHub
   - New → Web Service
   - Connect repository
   - Settings:
     - **Name:** scems-supervisor
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn supervisor.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `PORT=10000`
   - Deploy!

3. **Deploy Agent:**
   - New → Web Service (same repo)
   - Settings:
     - **Name:** scems-agent
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables:
     - `PORT=10001`
     - `SUPERVISOR_URL=https://scems-supervisor.onrender.com`
   - Deploy!

4. **Update Supervisor URL:**
   - After Agent deploys, update Supervisor's environment:
     - `AGENT_URL=https://scems-agent.onrender.com`

---

## 🔄 Alternative: Single Service Deployment

If platforms limit free services, you can combine both into one:

**Create `combined_main.py`:**
```python
import uvicorn
from multiprocessing import Process
import time

def run_supervisor():
    uvicorn.run("supervisor.main:app", host="0.0.0.0", port=8000)

def run_agent():
    time.sleep(2)  # Wait for supervisor
    uvicorn.run("agents.smart_campus_energy_agent.main:app", host="0.0.0.0", port=8001)

if __name__ == "__main__":
    p1 = Process(target=run_supervisor)
    p2 = Process(target=run_agent)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

---

## 📝 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Requirements.txt complete
- [ ] Environment variables configured
- [ ] Services deployed
- [ ] URLs noted
- [ ] Agent registered with Supervisor
- [ ] Test queries working

---

## 🌐 Quick Comparison

| Platform | Free Tier | Credit Card | Ease | Multi-Service |
|----------|-----------|-------------|------|---------------|
| **Render** | ✅ | ❌ | ⭐⭐⭐⭐⭐ | ✅ |
| **Koyeb** | ✅ | ❌ | ⭐⭐⭐⭐ | ✅ |
| **PythonAnywhere** | ✅ | ❌ | ⭐⭐⭐ | ⚠️ |
| **Replit** | ✅ | ❌ | ⭐⭐⭐⭐ | ✅ |
| **Cyclic** | ✅ | ❌ | ⭐⭐⭐ | ⚠️ |

---

## 💡 My Recommendation

**Use Render** - It's the easiest and most reliable for your use case:
- No credit card needed
- Easy GitHub integration
- Can deploy both services separately
- Good free tier
- Automatic HTTPS

---

## 🆘 Need Help?

If you encounter issues:
1. Check platform logs
2. Verify environment variables
3. Ensure ports are configured correctly
4. Check that both services can communicate

Good luck with your deployment! 🚀


