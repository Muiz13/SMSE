#!/bin/bash
# Automated demo script for SCEMS Multi-Agent System

set -e  # Exit on error

echo "=========================================="
echo "SCEMS Multi-Agent System Demo"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Generate synthetic data
echo -e "${BLUE}Step 1: Generating synthetic building energy data...${NC}"
python agents/smart_campus_energy_agent/sample_data/generator.py --days 30 --output-dir ./sample_data
echo -e "${GREEN}✓ Data generation complete${NC}"
echo ""

# Step 2: Train ML model
echo -e "${BLUE}Step 2: Training forecast model...${NC}"
python agents/smart_campus_energy_agent/model_stub.py --train ./sample_data/building_energy.csv ./models/forecast_model.pkl
echo -e "${GREEN}✓ Model training complete${NC}"
echo ""

# Step 3: Start Supervisor in background
echo -e "${BLUE}Step 3: Starting Supervisor service...${NC}"
python -m uvicorn supervisor.main:app --host 0.0.0.0 --port 8000 > supervisor.log 2>&1 &
SUPERVISOR_PID=$!
sleep 3
echo -e "${GREEN}✓ Supervisor started (PID: $SUPERVISOR_PID)${NC}"
echo ""

# Step 4: Start Agent in background
echo -e "${BLUE}Step 4: Starting Worker Agent...${NC}"
python -m uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port 8001 > agent.log 2>&1 &
AGENT_PID=$!
sleep 3
echo -e "${GREEN}✓ Agent started (PID: $AGENT_PID)${NC}"
echo ""

# Step 5: Wait for services to be ready
echo -e "${BLUE}Step 5: Waiting for services to be ready...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null && curl -s http://localhost:8001/health > /dev/null; then
        echo -e "${GREEN}✓ Services are ready${NC}"
        break
    fi
    sleep 1
done
echo ""

# Step 6: Register agent (if not auto-registered)
echo -e "${BLUE}Step 6: Registering agent with Supervisor...${NC}"
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
  }' > /dev/null 2>&1
echo -e "${GREEN}✓ Agent registered${NC}"
echo ""

# Step 7: Run sample queries
echo -e "${BLUE}Step 7: Running sample queries...${NC}"
echo ""

echo -e "${YELLOW}Query 1: Building Energy Analysis${NC}"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "prompt": "Analyze energy consumption for Building A today"
  }' | python -m json.tool
echo ""

echo -e "${YELLOW}Query 2: Energy Saving Recommendations${NC}"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "prompt": "What are energy saving recommendations for Building B?"
  }' | python -m json.tool
echo ""

echo -e "${YELLOW}Query 3: Peak Load Forecasting${NC}"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "prompt": "Forecast peak load for Building A for the next 24 hours"
  }' | python -m json.tool
echo ""

# Step 8: Show registry
echo -e "${BLUE}Step 8: Agent Registry${NC}"
curl -s http://localhost:8000/registry | python -m json.tool
echo ""

# Step 9: Aggregate health check
echo -e "${BLUE}Step 9: Aggregate Health Status${NC}"
curl -s http://localhost:8000/health/aggregate | python -m json.tool
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    kill $SUPERVISOR_PID 2>/dev/null || true
    kill $AGENT_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Demo complete${NC}"
}

# Trap to cleanup on exit
trap cleanup EXIT

echo ""
echo -e "${GREEN}=========================================="
echo "Demo completed successfully!"
echo "==========================================${NC}"
echo ""
echo "Services are still running. Press Ctrl+C to stop."
echo "Supervisor UI: http://localhost:8000/ui"
echo "Supervisor API: http://localhost:8000/docs"
echo "Agent API: http://localhost:8001/docs"
echo ""

# Keep script running
wait

