"""
Abstract base class for worker agents in the multi-agent system.

Provides common functionality for task processing, message handling,
and communication with the Supervisor agent.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx
from shared.protocol import TaskAssignment, CompletionReport, create_completion_report
from shared.utils import iso_now, log_json, safe_json_loads

logger = logging.getLogger(__name__)


class AbstractWorkerAgent(ABC):
    """
    Abstract base class for all worker agents.
    
    Subclasses must implement:
    - process_task(): Execute the actual task logic
    - get_capabilities(): Return list of supported capabilities
    """
    
    def __init__(
        self,
        agent_name: str,
        supervisor_url: str,
        ltm: Optional[Any] = None
    ):
        """
        Initialize the worker agent.
        
        Args:
            agent_name: Unique identifier for this agent
            supervisor_url: Base URL of the Supervisor service
            ltm: Long-term memory instance (optional)
        """
        self.agent_name = agent_name
        self.supervisor_url = supervisor_url
        self.ltm = ltm
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
    
    @abstractmethod
    def process_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and return results.
        
        Args:
            task_name: Name of the task to execute
            parameters: Task-specific parameters
            
        Returns:
            Dictionary containing:
            - data: Task results
            - explainability: List of explanation strings
            - ltm_hit: Boolean indicating if result came from LTM
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Get list of capabilities this agent supports.
        
        Returns:
            List of capability names
        """
        pass
    
    def handle_task_assignment(self, assignment: TaskAssignment) -> CompletionReport:
        """
        Handle an incoming task assignment message.
        
        Args:
            assignment: Task assignment message from Supervisor
            
        Returns:
            Completion report with task results
        """
        self.logger.info(
            f"Received task assignment",
            extra={
                "message_id": assignment.message_id,
                "task_name": assignment.task.name,
                "priority": assignment.task.priority
            }
        )
        
        try:
            # Check LTM for cached results
            ltm_hit = False
            ltm_key = self._generate_ltm_key(assignment.task.name, assignment.task.parameters.data)
            
            if self.ltm:
                cached_result = self.ltm.read(ltm_key)
                if cached_result:
                    self.logger.info(f"LTM cache hit for key: {ltm_key}")
                    ltm_hit = True
                    results = cached_result
                else:
                    # Execute task
                    results = self.process_task(
                        assignment.task.name,
                        assignment.task.parameters.data
                    )
                    # Store in LTM
                    self.ltm.write(ltm_key, results)
            else:
                # No LTM, execute directly
                results = self.process_task(
                    assignment.task.name,
                    assignment.task.parameters.data
                )
            
            # Ensure results have required structure
            if "ltm_hit" not in results:
                results["ltm_hit"] = ltm_hit
            
            completion_report = create_completion_report(
                sender=self.agent_name,
                recipient=assignment.sender,
                related_message_id=assignment.message_id,
                status="SUCCESS",
                results=results
            )
            
            self.logger.info(
                f"Task completed successfully",
                extra={"message_id": assignment.message_id, "status": "SUCCESS"}
            )
            
            return completion_report
            
        except Exception as e:
            self.logger.error(
                f"Task execution failed: {str(e)}",
                extra={"message_id": assignment.message_id},
                exc_info=True
            )
            
            completion_report = create_completion_report(
                sender=self.agent_name,
                recipient=assignment.sender,
                related_message_id=assignment.message_id,
                status="FAILURE",
                results={},
                error=str(e)
            )
            
            return completion_report
    
    def _execute_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to execute task (wrapper around process_task).
        
        Args:
            task_name: Name of the task
            parameters: Task parameters
            
        Returns:
            Task results dictionary
        """
        return self.process_task(task_name, parameters)
    
    def send_message(self, message: CompletionReport) -> bool:
        """
        Send a completion report message to the Supervisor.
        
        Args:
            message: Completion report to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Supervisor endpoint for receiving reports (if implemented)
            # For now, this is a placeholder - actual reporting happens via HTTP response
            report_url = f"{self.supervisor_url}/report"
            
            self.logger.info(
                f"Sending completion report to Supervisor",
                extra={
                    "message_id": message.message_id,
                    "related_message_id": message.related_message_id,
                    "status": message.status
                }
            )
            
            # In a full implementation, this would POST to Supervisor
            # For now, we'll log it
            log_json(
                "completion_report_sent",
                message_id=message.message_id,
                status=message.status,
                recipient=message.recipient
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to Supervisor: {str(e)}", exc_info=True)
            return False
    
    def _report_completion(
        self,
        related_message_id: str,
        status: str,
        results: Dict[str, Any],
        error: Optional[str] = None
    ) -> CompletionReport:
        """
        Create and send a completion report.
        
        Args:
            related_message_id: Original task assignment message ID
            status: SUCCESS or FAILURE
            results: Task results
            error: Error message if status is FAILURE
            
        Returns:
            Completion report message
        """
        report = create_completion_report(
            sender=self.agent_name,
            recipient="SupervisorAgent_Main",
            related_message_id=related_message_id,
            status=status,
            results=results,
            error=error
        )
        
        self.send_message(report)
        return report
    
    def _generate_ltm_key(self, task_name: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a canonical LTM key from task name and parameters.
        
        Args:
            task_name: Name of the task
            parameters: Task parameters
            
        Returns:
            Canonical key string
        """
        # Create a deterministic key from task and key parameters
        key_parts = [task_name]
        
        # Include relevant parameters in key
        if "building_id" in parameters:
            key_parts.append(parameters["building_id"])
        if "date" in parameters:
            key_parts.append(parameters["date"])
        elif "start_date" in parameters:
            key_parts.append(parameters["start_date"])
        
        return ":".join(key_parts)
    
    def parse_message(self, message_data: str) -> Optional[TaskAssignment]:
        """
        Parse a JSON message string into a TaskAssignment.
        
        Args:
            message_data: JSON string or dictionary
            
        Returns:
            TaskAssignment object or None if parsing fails
        """
        try:
            if isinstance(message_data, str):
                data = safe_json_loads(message_data)
            else:
                data = message_data
            
            if data is None:
                return None
            
            return TaskAssignment(**data)
            
        except Exception as e:
            self.logger.error(f"Failed to parse message: {str(e)}", exc_info=True)
            return None

