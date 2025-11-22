"""
FastAPI application for Smart Campus Energy Management Agent.

Exposes REST API endpoints for task execution and agent management.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from shared.utils import load_config, setup_logging
from shared.protocol import TaskAssignment
from .agent import SmartCampusEnergyAgent
from .ltm import LTM
from .schemas import (
    HealthResponse,
    CapabilitiesResponse,
    TaskRequest,
    TaskResponse,
    SyncTaskResponse
)

# Load configuration
config = load_config()
setup_logging(
    level=config.get("logging", {}).get("level", "INFO"),
    format_type=config.get("logging", {}).get("format", "json")
)

logger = logging.getLogger(__name__)

# Initialize LTM
ltm_type = config.get("ltm", {}).get("type", "sqlite")
ltm_path = config.get("ltm", {}).get("path", "./ltm.db")
ltm = LTM(backend_type=ltm_type, path=ltm_path)

# Initialize agent
supervisor_url = config.get("agent", {}).get("supervisor_url", "http://localhost:8000")
agent_name = config.get("agent", {}).get("name", "SmartCampusEnergyAgent")
model_path = config.get("ml", {}).get("model_path", "./models/forecast_model.pkl")
data_dir = config.get("data", {}).get("sample_data_dir", "./sample_data")

agent = SmartCampusEnergyAgent(
    agent_name=agent_name,
    supervisor_url=supervisor_url,
    ltm=ltm,
    model_path=model_path,
    data_dir=data_dir
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info(f"Starting {agent_name}")
    
    # Auto-register with Supervisor (optional)
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            registration_data = {
                "name": agent_name,
                "base_url": config.get("agent", {}).get("base_url", "http://localhost:8001"),
                "health_url": f"{config.get('agent', {}).get('base_url', 'http://localhost:8001')}/health",
                "capabilities": agent.get_capabilities()
            }
            response = await client.post(
                f"{supervisor_url}/register",
                json=registration_data,
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info("Successfully auto-registered with Supervisor")
            else:
                logger.warning(f"Auto-registration failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"Auto-registration skipped: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {agent_name}")
    ltm.close()


app = FastAPI(
    title="Smart Campus Energy Management Agent",
    description="Worker agent for campus energy management tasks",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="up", agent=agent_name)


@app.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """Get list of agent capabilities."""
    return CapabilitiesResponse(capabilities=agent.get_capabilities())


@app.post("/task", response_model=TaskResponse)
async def execute_task_async(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a task asynchronously.
    
    Accepts a task assignment and returns immediate acknowledgment.
    Task execution happens in the background.
    """
    try:
        # Convert request to TaskAssignment
        assignment = TaskAssignment(
            message_id=request.message_id or TaskAssignment().message_id,
            sender=request.sender,
            recipient=request.recipient,
            type=request.type,
            task=request.task,
            timestamp=request.timestamp or TaskAssignment().timestamp
        )
        
        # Schedule background task
        background_tasks.add_task(process_task_background, assignment)
        
        return TaskResponse(
            status="accepted",
            message_id=assignment.message_id,
            message="Task queued for execution"
        )
        
    except Exception as e:
        logger.error(f"Task acceptance failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


async def process_task_background(assignment: TaskAssignment):
    """Background task processor."""
    try:
        completion_report = agent.handle_task_assignment(assignment)
        # In a full implementation, this would POST back to Supervisor
        logger.info(f"Task completed: {assignment.message_id}")
    except Exception as e:
        logger.error(f"Background task failed: {e}", exc_info=True)


@app.post("/task/sync", response_model=SyncTaskResponse)
async def execute_task_sync(request: TaskRequest):
    """
    Execute a task synchronously.
    
    Accepts a task assignment and returns completion report in response.
    """
    try:
        # Convert request to TaskAssignment
        assignment = TaskAssignment(
            message_id=request.message_id or TaskAssignment().message_id,
            sender=request.sender,
            recipient=request.recipient,
            type=request.type,
            task=request.task,
            timestamp=request.timestamp or TaskAssignment().timestamp
        )
        
        # Process task
        completion_report = agent.handle_task_assignment(assignment)
        
        # Convert to response format
        return SyncTaskResponse(
            message_id=completion_report.message_id,
            sender=completion_report.sender,
            recipient=completion_report.recipient,
            type=completion_report.type,
            related_message_id=completion_report.related_message_id,
            status=completion_report.status,
            results=completion_report.results,
            timestamp=completion_report.timestamp,
            error=completion_report.error
        )
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", config.get("agent", {}).get("port", 8001)))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

