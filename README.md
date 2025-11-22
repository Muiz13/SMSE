# Smart Campus Energy Management Agent (SCEMS) - Multi-Agent System

A production-ready FastAPI-based multi-agent system implementing a Supervisor–Worker architecture for intelligent campus energy management.

## Project Overview

This repository implements a multi-agent system where a Supervisor agent coordinates with specialized worker agents to provide comprehensive energy management capabilities for smart campuses. The primary worker agent is the **Smart Campus Energy Management Agent** (SCEMS) with the following capabilities:

- `building_energy_analysis`: Analyze energy consumption patterns for buildings
- `appliance_energy_breakdown`: Break down energy usage by appliance type
- `peak_load_forecasting`: Forecast peak energy demand using ML models
- `energy_saving_recommendations`: Provide actionable energy-saving recommendations
- `solar_energy_estimation`: Estimate solar energy generation potential
- `cost_estimation`: Calculate energy costs and savings

## Repository Structure

```
scems-mas/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image definition
├── docker-compose.yml           # Multi-service orchestration
├── supervisor/                  # Supervisor service
│   ├── main.py                 # FastAPI app (Supervisor & Registry)
│   ├── supervisor.py           # Routing, intent detection, registry
│   ├── registry.json           # Agent registry storage
│   ├── schemas.py              # Pydantic models for messages
│   ├── templates/               # Web UI templates
│   └── tests/                  # Supervisor tests
├── agents/                      # Worker agents
│   └── smart_campus_energy_agent/
│       ├── main.py             # FastAPI worker endpoints
│       ├── agent.py            # SCEMS agent implementation
│       ├── worker_base.py      # AbstractWorkerAgent base class
│       ├── ltm.py              # Long-term memory (SQLite/file)
│       ├── model_stub.py       # ML forecasting & optimization
│       ├── schemas.py          # Local request/response models
│       ├── sample_data/        # Synthetic data generator
│       └── tests/              # Agent tests
├── shared/                      # Shared utilities
│   ├── protocol.py             # JSON message contracts
│   ├── utils.py                # Logging, time helpers, config
│   └── config.yaml             # Default configuration
├── ci/                          # CI/CD
│   └── pipeline.yml            # GitHub Actions example
├── docs/                        # Documentation
│   └── assignment_spec.pdf     # Project specification reference
├── demo/                        # Demo scripts
│   └── run_demo.sh             # Automated demo runner
└── EXAMPLE_REQUESTS.md          # Sample API requests

```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker and Docker Compose (optional, for containerized deployment)

### Local Development Setup

1. **Clone and navigate to the repository:**
   ```bash
   cd scems-mas
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Generate synthetic data (optional):**
   ```bash
   python agents/smart_campus_energy_agent/sample_data/generator.py
   ```

6. **Train ML model stub (optional):**
   ```bash
   python agents/smart_campus_energy_agent/model_stub.py --train
   ```

7. **Start Supervisor service:**
   ```bash
   uvicorn supervisor.main:app --reload --port 8000
   ```

8. **Start Worker Agent (in a separate terminal):**
   ```bash
   uvicorn agents.smart_campus_energy_agent.main:app --reload --port 8001
   ```

9. **Register the agent with Supervisor:**
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

10. **Test the system:**
    ```bash
    curl -X POST http://localhost:8000/query \
      -H "Content-Type: application/json" \
      -d '{
        "user_id": "test_user",
        "prompt": "Analyze energy consumption for Building A today"
      }'
    ```

### Running Tests

Run all tests:
```bash
pytest -q
```

Run specific test suite:
```bash
pytest supervisor/tests/
pytest agents/smart_campus_energy_agent/tests/
```

### Docker Deployment

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access services:**
   - Supervisor API: http://localhost:8000
   - Worker Agent API: http://localhost:8001
   - Supervisor UI: http://localhost:8000/ui

3. **Stop services:**
   ```bash
   docker-compose down
   ```

### Automated Demo

Run the complete demo script:
```bash
bash demo/run_demo.sh
```

Or on Windows (PowerShell):
```powershell
.\demo\run_demo.ps1
```

## API Endpoints

### Supervisor Endpoints

- `GET /health` - Health check
- `GET /registry` - List registered agents
- `POST /register` - Register a new agent
- `POST /query` - Natural language query routing
- `GET /health/aggregate` - Aggregate health status of all agents
- `GET /ui` - Web UI for manual agent management

### Worker Agent Endpoints

- `GET /health` - Health check
- `GET /capabilities` - List agent capabilities
- `POST /task` - Asynchronous task execution
- `POST /task/sync` - Synchronous task execution
- `GET /docs` - OpenAPI documentation

See `EXAMPLE_REQUESTS.md` for detailed request examples.

## Message Protocol

All inter-service communication follows a standardized JSON message format:

**Task Assignment (Supervisor → Worker):**
```json
{
  "message_id": "<uuid>",
  "sender": "SupervisorAgent_Main",
  "recipient": "SmartCampusEnergyAgent",
  "type": "task_assignment",
  "task": {
    "name": "building_energy_analysis",
    "priority": 2,
    "parameters": { ... }
  },
  "timestamp": "2025-11-22T18:00:00Z"
}
```

**Completion Report (Worker → Supervisor):**
```json
{
  "message_id": "<uuid>",
  "sender": "SmartCampusEnergyAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "completion_report",
  "related_message_id": "<uuid>",
  "status": "SUCCESS",
  "results": {
    "data": { ... },
    "explainability": [ ... ],
    "ltm_hit": false
  },
  "timestamp": "2025-11-22T18:00:10Z"
}
```

## Deliverable Mapping

### Assignment 01: Project Charter & Lifecycle
- **Artifacts**: `README.md`, `docs/assignment_spec.pdf`
- **Description**: Project overview, goals, and lifecycle documentation

### Assignment 02: Scope & WBS
- **Artifacts**: `shared/config.yaml`, `supervisor/registry.json`
- **Description**: System scope defined through configuration and registry structure

### Assignment 03: Schedule, AON, Costing
- **Artifacts**: `ci/pipeline.yml`, `README.md`, `docs/evm_example.md`
- **Description**: CI/CD pipeline represents schedule, EVM tracking documented

### Final Deliverable
- **Code**: Complete repository with all components
- **Report**: See `docs/` directory
- **Demo**: `demo/run_demo.sh` provides automated demonstration

## Configuration

Configuration is managed through:
- `shared/config.yaml` - Default configuration
- Environment variables (override defaults):
  - `SUPERVISOR_HOST` - Supervisor host (default: localhost)
  - `SUPERVISOR_PORT` - Supervisor port (default: 8000)
  - `AGENT_HOST` - Agent host (default: localhost)
  - `AGENT_PORT` - Agent port (default: 8001)
  - `LTM_TYPE` - LTM backend: `sqlite` or `file` (default: sqlite)
  - `LTM_PATH` - LTM storage path (default: `./ltm.db` or `./ltm.json`)

## Long-Term Memory (LTM)

The agent implements a SQLite-backed LTM with file-based fallback:
- Stores task results with timestamps
- Supports key-value storage and prefix queries
- Automatic TTL-based cleanup
- Fallback to JSON file storage if SQLite unavailable

## ML Model Stub

The forecasting capability uses a lightweight scikit-learn LinearRegression model:
- Trained on synthetic time-series features (hour, day-of-week, historical consumption)
- Model persisted to disk for reuse
- Deterministic formulas for solar estimation
- Heuristic-based recommendations

## Security & Safety

- All endpoints validate input using Pydantic models
- No real private data required (synthetic data by default)
- No external API dependencies (except optional weather API)
- Input validation returns 4xx errors on invalid JSON
- Environment-based configuration for sensitive settings

## Development

### Code Structure
- Modular design with clear separation of concerns
- Type hints throughout
- Comprehensive docstrings
- Pydantic models for all external schemas

### Logging
- Structured JSON logging
- Request/response logging for all messages
- Error tracking and metrics

### Testing
- Unit tests for core components
- Integration tests for API endpoints
- Mock-based testing for external dependencies

## License

This project is created for academic purposes as part of the FSPM-1 course.

## Contributors

- i202318
- i222632
- i222462

## References

- Project Specification: `docs/assignment_spec.pdf`
- Example Requests: `EXAMPLE_REQUESTS.md`
- Sample Prompts: `SAMPLE_PROMPT_FOR_CURSOR.txt`

