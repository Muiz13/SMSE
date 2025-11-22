"""
FastAPI application for Supervisor agent.

Manages agent registry, routes queries, and provides web UI.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from shared.utils import load_config, setup_logging, iso_now
from .supervisor import Supervisor
from .schemas import (
    HealthResponse,
    RegisterRequest,
    RegistryResponse,
    QueryRequest,
    QueryResponse,
    AggregateHealthResponse
)

# Load configuration
config = load_config()
setup_logging(
    level=config.get("logging", {}).get("level", "INFO"),
    format_type=config.get("logging", {}).get("format", "json")
)

logger = logging.getLogger(__name__)

# Initialize Supervisor
registry_path = os.getenv("REGISTRY_PATH", "./supervisor/registry.json")
supervisor = Supervisor(registry_path=registry_path)

# Initialize FastAPI app
app = FastAPI(
    title="Supervisor Agent",
    description="Multi-agent system supervisor and registry",
    version="1.0.0"
)

# Templates for web UI
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.get("/registry", response_model=RegistryResponse)
async def get_registry():
    """Get list of all registered agents."""
    agents = supervisor.get_registry()
    return RegistryResponse(agents=agents, total=len(agents))


@app.post("/register")
async def register_agent(request: RegisterRequest):
    """
    Register a new agent or update existing registration.
    
    Request body:
    {
      "name": "SmartCampusEnergyAgent",
      "base_url": "http://localhost:8001",
      "health_url": "http://localhost:8001/health",
      "capabilities": ["building_energy_analysis", ...]
    }
    """
    success = supervisor.register_agent(request)
    if success:
        return {"status": "registered", "agent": request.name}
    else:
        raise HTTPException(status_code=400, detail="Registration failed")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Route a natural language query to appropriate agent.
    
    Request body:
    {
      "user_id": "user123",
      "prompt": "Analyze energy consumption for Building A today"
    }
    """
    try:
        result = await supervisor.route_query(request.prompt, request.user_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result)
        
        return QueryResponse(
            agent=result["agent"],
            capability=result["capability"],
            response=result["response"],
            timestamp=iso_now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health/aggregate", response_model=AggregateHealthResponse)
async def aggregate_health():
    """Get aggregate health status of all registered agents."""
    result = await supervisor.aggregate_health()
    return AggregateHealthResponse(**result)


@app.get("/ui", response_class=HTMLResponse)
async def web_ui(request: Request):
    """Simple web UI for agent management."""
    try:
        agents = supervisor.get_registry()
        return templates.TemplateResponse(
            "ui.html",
            {
                "request": request,
                "agents": agents,
                "total_agents": len(agents)
            }
        )
    except Exception as e:
        logger.error(f"UI error: {e}", exc_info=True)
        # Return a simple HTML error page
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error Loading UI</h1>
                    <p>Error: {str(e)}</p>
                    <p>Template directory: {templates_dir}</p>
                    <p>Template exists: {templates_dir.exists()}</p>
                    <p><a href="/docs">Go to API Docs</a></p>
                </body>
            </html>
            """,
            status_code=500
        )


@app.post("/ui/query")
async def ui_query(request: Request):
    """Handle query from web UI."""
    try:
        # Parse form data
        try:
            form = await request.form()
            prompt = form.get("prompt", "")
            user_id = form.get("user_id", "web_user")
        except Exception as form_error:
            logger.error(f"Form parsing error: {form_error}", exc_info=True)
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Failed to parse form data: {str(form_error)}",
                    "status_code": 400
                }
            )
        
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Prompt is required",
                    "status_code": 400
                }
            )
        
        # Route the query
        try:
            result = await supervisor.route_query(prompt, user_id)
        except Exception as route_error:
            logger.error(f"Route query error: {route_error}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to route query: {str(route_error)}",
                    "type": type(route_error).__name__,
                    "status_code": 500
                }
            )
        
        if "error" in result:
            return JSONResponse(
                status_code=404,
                content={
                    "error": result.get("error", "Unknown error"),
                    "suggestions": result.get("suggestions", []),
                    "status_code": 404
                }
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"UI query error: {e}", exc_info=True)
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "status_code": 500,
                "message": "An error occurred while processing your query"
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "status_code": 500,
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("SUPERVISOR_PORT", config.get("supervisor", {}).get("port", 8000)))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

