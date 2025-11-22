"""
Pydantic schemas for Supervisor API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok", description="Service status")


class AgentMetadata(BaseModel):
    """Agent registration metadata."""
    name: str = Field(..., description="Agent name")
    base_url: str = Field(..., description="Agent base URL")
    health_url: str = Field(..., description="Agent health check URL")
    capabilities: List[str] = Field(..., description="List of agent capabilities")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")


class RegisterRequest(BaseModel):
    """Agent registration request."""
    name: str = Field(..., description="Agent name")
    base_url: str = Field(..., description="Agent base URL")
    health_url: str = Field(..., description="Agent health check URL")
    capabilities: List[str] = Field(..., description="List of agent capabilities")


class RegistryResponse(BaseModel):
    """Registry listing response."""
    agents: List[AgentMetadata] = Field(..., description="List of registered agents")
    total: int = Field(..., description="Total number of agents")


class QueryRequest(BaseModel):
    """Natural language query request."""
    user_id: str = Field(..., description="User identifier")
    prompt: str = Field(..., description="Natural language query")


class QueryResponse(BaseModel):
    """Query response."""
    agent: str = Field(..., description="Agent that handled the query")
    capability: str = Field(..., description="Capability used")
    response: Dict[str, Any] = Field(..., description="Agent response")
    timestamp: str = Field(..., description="Response timestamp")


class AggregateHealthResponse(BaseModel):
    """Aggregate health status response."""
    supervisor_status: str = Field(default="ok")
    agents: List[Dict[str, Any]] = Field(..., description="Individual agent health statuses")
    total_agents: int = Field(..., description="Total number of agents")
    healthy_agents: int = Field(..., description="Number of healthy agents")

