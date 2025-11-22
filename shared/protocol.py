"""
Shared message protocol definitions for Supervisor-Worker communication.

Defines the JSON message contract used for all inter-agent communication
following a standardized request/response format.
"""

from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class TaskParameters(BaseModel):
    """Domain-specific task parameters."""
    # Flexible structure to accommodate different task types
    data: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """Task definition within a task assignment."""
    name: str = Field(..., description="Task name matching agent capability")
    priority: int = Field(default=2, ge=1, le=5, description="Task priority (1-5)")
    parameters: TaskParameters = Field(default_factory=TaskParameters)


class TaskAssignment(BaseModel):
    """
    Supervisor -> Worker: Task assignment message.
    
    Example:
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440000",
      "sender": "SupervisorAgent_Main",
      "recipient": "SmartCampusEnergyAgent",
      "type": "task_assignment",
      "task": {
        "name": "building_energy_analysis",
        "priority": 2,
        "parameters": {
          "data": {
            "building_id": "Building-A",
            "date": "2025-11-22"
          }
        }
      },
      "timestamp": "2025-11-22T18:00:00Z"
    }
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = Field(..., description="Sender agent identifier")
    recipient: str = Field(..., description="Recipient agent identifier")
    type: str = Field(default="task_assignment", description="Message type")
    task: Task = Field(..., description="Task to be executed")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO 8601 timestamp"
    )


class CompletionReport(BaseModel):
    """
    Worker -> Supervisor: Task completion report.
    
    Example:
    {
      "message_id": "660e8400-e29b-41d4-a716-446655440001",
      "sender": "SmartCampusEnergyAgent",
      "recipient": "SupervisorAgent_Main",
      "type": "completion_report",
      "related_message_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "SUCCESS",
      "results": {
        "data": {
          "total_consumption_kwh": 1250.5,
          "peak_hour": 14
        },
        "explainability": [
          "Analyzed 24-hour consumption data",
          "Peak consumption occurred at 2 PM"
        ],
        "ltm_hit": false
      },
      "timestamp": "2025-11-22T18:00:10Z"
    }
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = Field(..., description="Sender agent identifier")
    recipient: str = Field(..., description="Recipient agent identifier")
    type: str = Field(default="completion_report", description="Message type")
    related_message_id: str = Field(..., description="Original task assignment message ID")
    status: str = Field(..., description="SUCCESS or FAILURE")
    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Task results including 'data', 'explainability', and 'ltm_hit'"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO 8601 timestamp"
    )
    error: Optional[str] = Field(None, description="Error message if status is FAILURE")


def create_task_assignment(
    sender: str,
    recipient: str,
    task_name: str,
    parameters: Dict[str, Any],
    priority: int = 2
) -> TaskAssignment:
    """Helper function to create a task assignment message."""
    return TaskAssignment(
        sender=sender,
        recipient=recipient,
        task=Task(
            name=task_name,
            priority=priority,
            parameters=TaskParameters(data=parameters)
        )
    )


def create_completion_report(
    sender: str,
    recipient: str,
    related_message_id: str,
    status: str,
    results: Dict[str, Any],
    error: Optional[str] = None
) -> CompletionReport:
    """Helper function to create a completion report message."""
    return CompletionReport(
        sender=sender,
        recipient=recipient,
        related_message_id=related_message_id,
        status=status,
        results=results,
        error=error
    )

