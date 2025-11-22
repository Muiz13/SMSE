# Example API Requests

This document provides sample curl commands and expected outputs for testing the SCEMS Multi-Agent System.

## Prerequisites

- Supervisor running on `http://localhost:8000`
- Worker Agent running on `http://localhost:8001`
- Agent registered with Supervisor

## Supervisor Endpoints

### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

### 2. Register Agent

```bash
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
  }'
```

**Expected Response:**
```json
{
  "status": "registered",
  "agent": "SmartCampusEnergyAgent"
}
```

### 3. List Registered Agents

```bash
curl -X GET http://localhost:8000/registry
```

**Expected Response:**
```json
{
  "agents": [
    {
      "name": "SmartCampusEnergyAgent",
      "base_url": "http://localhost:8001",
      "health_url": "http://localhost:8001/health",
      "capabilities": [...],
      "last_seen": "2025-11-22T18:00:00Z"
    }
  ],
  "total": 1
}
```

### 4. Natural Language Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt": "Analyze energy consumption for Building A today"
  }'
```

**Expected Response:**
```json
{
  "agent": "SmartCampusEnergyAgent",
  "capability": "building_energy_analysis",
  "response": {
    "message_id": "...",
    "status": "SUCCESS",
    "results": {
      "data": {
        "building_id": "Building-A",
        "date": "2025-11-22",
        "total_consumption_kwh": 1250.5,
        "peak_hour": 14,
        "average_consumption_kwh": 52.1
      },
      "explainability": [...],
      "ltm_hit": false
    }
  },
  "timestamp": "2025-11-22T18:00:00Z"
}
```

### 5. Aggregate Health Check

```bash
curl -X GET http://localhost:8000/health/aggregate
```

**Expected Response:**
```json
{
  "supervisor_status": "ok",
  "agents": [
    {
      "name": "SmartCampusEnergyAgent",
      "status": "healthy",
      "response_time_ms": 15.23
    }
  ],
  "total_agents": 1,
  "healthy_agents": 1
}
```

## Worker Agent Endpoints

### 1. Health Check

```bash
curl -X GET http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "up",
  "agent": "SmartCampusEnergyAgent"
}
```

### 2. Get Capabilities

```bash
curl -X GET http://localhost:8001/capabilities
```

**Expected Response:**
```json
{
  "capabilities": [
    "building_energy_analysis",
    "appliance_energy_breakdown",
    "peak_load_forecasting",
    "energy_saving_recommendations",
    "solar_energy_estimation",
    "cost_estimation"
  ]
}
```

### 3. Execute Task (Synchronous)

```bash
curl -X POST http://localhost:8001/task/sync \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "SupervisorAgent_Main",
    "recipient": "SmartCampusEnergyAgent",
    "type": "task_assignment",
    "task": {
      "name": "building_energy_analysis",
      "priority": 2,
      "parameters": {
        "data": {
          "building_id": "Building-A",
          "date": "today"
        }
      }
    }
  }'
```

**Expected Response:**
```json
{
  "message_id": "...",
  "sender": "SmartCampusEnergyAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "completion_report",
  "related_message_id": "...",
  "status": "SUCCESS",
  "results": {
    "data": {...},
    "explainability": [...],
    "ltm_hit": false
  },
  "timestamp": "2025-11-22T18:00:10Z"
}
```

### 4. Execute Task (Asynchronous)

```bash
curl -X POST http://localhost:8001/task \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "SupervisorAgent_Main",
    "recipient": "SmartCampusEnergyAgent",
    "type": "task_assignment",
    "task": {
      "name": "peak_load_forecasting",
      "priority": 2,
      "parameters": {
        "data": {
          "building_id": "Building-A",
          "forecast_hours": 24
        }
      }
    }
  }'
```

**Expected Response:**
```json
{
  "status": "accepted",
  "message_id": "...",
  "message": "Task queued for execution"
}
```

## Example Queries by Capability

### Building Energy Analysis

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "How much energy did Building A consume today?"
  }'
```

### Appliance Energy Breakdown

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "Show me the energy breakdown by appliance for Building B"
  }'
```

### Peak Load Forecasting

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "Forecast peak load for Building A for the next 24 hours"
  }'
```

### Energy Saving Recommendations

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "What are some energy saving recommendations for Building C?"
  }'
```

### Solar Energy Estimation

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "Estimate solar energy generation for 100kW panels"
  }'
```

### Cost Estimation

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "What is the cost for 1000 kWh consumption at $0.12 per kWh?"
  }'
```

## Error Handling

### Invalid Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "prompt": "What is the weather today?"
  }'
```

**Expected Response:**
```json
{
  "detail": {
    "error": "No agent found to handle this query",
    "suggestions": [...]
  }
}
```

### Invalid JSON

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}'
```

**Expected Response:**
```json
{
  "detail": "Invalid JSON"
}
```

