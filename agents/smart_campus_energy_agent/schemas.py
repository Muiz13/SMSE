"""
Pydantic schemas for Smart Campus Energy Agent API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from shared.protocol import TaskAssignment, CompletionReport


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="up", description="Service status")
    agent: str = Field(default="SmartCampusEnergyAgent", description="Agent name")


class CapabilitiesResponse(BaseModel):
    """Capabilities list response."""
    capabilities: List[str] = Field(
        default=[
            "building_energy_analysis",
            "appliance_energy_breakdown",
            "peak_load_forecasting",
            "energy_saving_recommendations",
            "solar_energy_estimation",
            "cost_estimation"
        ],
        description="List of supported capabilities"
    )


class TaskRequest(BaseModel):
    """Request body for /task endpoint."""
    message_id: Optional[str] = None
    sender: str = Field(default="SupervisorAgent_Main")
    recipient: str = Field(default="SmartCampusEnergyAgent")
    type: str = Field(default="task_assignment")
    task: Dict[str, Any] = Field(..., description="Task definition")
    timestamp: Optional[str] = None


class TaskResponse(BaseModel):
    """Response from /task endpoint (async acknowledgment)."""
    status: str = Field(default="accepted", description="Task acceptance status")
    message_id: str = Field(..., description="Task assignment message ID")
    message: str = Field(default="Task queued for execution", description="Status message")


class SyncTaskResponse(BaseModel):
    """Response from /task/sync endpoint (synchronous completion)."""
    message_id: str = Field(..., description="Completion report message ID")
    sender: str = Field(default="SmartCampusEnergyAgent")
    recipient: str = Field(default="SupervisorAgent_Main")
    type: str = Field(default="completion_report")
    related_message_id: str = Field(..., description="Original task assignment ID")
    status: str = Field(..., description="SUCCESS or FAILURE")
    results: Dict[str, Any] = Field(..., description="Task results")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = None

