"""
Supervisor agent implementation.

Handles agent registry, intent detection, and task routing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from shared.protocol import TaskAssignment, create_task_assignment
from shared.utils import iso_now, log_json
from .schemas import AgentMetadata, RegisterRequest

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """
    Normalize URL to ensure it has a protocol prefix.
    
    Args:
        url: URL string (may or may not have protocol)
        
    Returns:
        URL with protocol prefix (https:// for Railway domains, http:// for localhost)
    """
    if not url:
        return url
    
    url = url.strip()
    
    # If already has protocol, return as is
    if url.startswith(("http://", "https://")):
        return url
    
    # For Railway domains or production domains, use https
    if ".railway.app" in url or ".up.railway.app" in url or ".herokuapp.com" in url or ".vercel.app" in url:
        return f"https://{url}"
    
    # For localhost, use http
    if "localhost" in url or "127.0.0.1" in url:
        return f"http://{url}"
    
    # Default to https for unknown domains
    return f"https://{url}"


class Supervisor:
    """
    Supervisor agent that manages worker agents and routes tasks.
    """
    
    def __init__(self, registry_path: str = "./supervisor/registry.json"):
        """
        Initialize Supervisor.
        
        Args:
            registry_path: Path to registry JSON file
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, AgentMetadata] = {}
        self.logger = logging.getLogger(f"{__name__}.Supervisor")
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load agent registry from file."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for agent_data in data.get("agents", []):
                        # Normalize URLs to ensure they have protocol
                        agent_data["base_url"] = normalize_url(agent_data.get("base_url", ""))
                        agent_data["health_url"] = normalize_url(agent_data.get("health_url", ""))
                        agent = AgentMetadata(**agent_data)
                        self.registry[agent.name] = agent
                self.logger.info(f"Loaded {len(self.registry)} agents from registry")
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}", exc_info=True)
                self.registry = {}
        else:
            self.registry = {}
            self._save_registry()
    
    def _save_registry(self) -> None:
        """Save agent registry to file."""
        try:
            agents_data = [
                {
                    "name": agent.name,
                    "base_url": agent.base_url,
                    "health_url": agent.health_url,
                    "capabilities": agent.capabilities,
                    "last_seen": agent.last_seen or iso_now()
                }
                for agent in self.registry.values()
            ]
            with open(self.registry_path, 'w') as f:
                json.dump({"agents": agents_data}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}", exc_info=True)
    
    def register_agent(self, request: RegisterRequest) -> bool:
        """
        Register a new agent or update existing registration.
        
        Args:
            request: Agent registration request
            
        Returns:
            True if successful
        """
        try:
            # Normalize URLs to ensure they have protocol
            normalized_base_url = normalize_url(request.base_url)
            normalized_health_url = normalize_url(request.health_url)
            
            agent = AgentMetadata(
                name=request.name,
                base_url=normalized_base_url,
                health_url=normalized_health_url,
                capabilities=request.capabilities,
                last_seen=iso_now()
            )
            
            self.registry[request.name] = agent
            self._save_registry()
            
            self.logger.info(
                f"Registered agent: {request.name}",
                extra={"capabilities": request.capabilities, "base_url": normalized_base_url}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Agent registration failed: {e}", exc_info=True)
            return False
    
    def get_registry(self) -> List[AgentMetadata]:
        """Get list of all registered agents."""
        return list(self.registry.values())
    
    def detect_intent(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Detect intent from natural language prompt.
        
        Maps keywords to agent capabilities and selects appropriate agent.
        Can detect multiple capabilities in a single query.
        
        Args:
            prompt: Natural language query
            
        Returns:
            Dictionary with 'agent_name', 'capability' (single) or 'capabilities' (multiple), and 'agent'
        """
        prompt_lower = prompt.lower()
        
        # Capability keyword mapping
        capability_keywords = {
            "building_energy_analysis": [
                "building", "energy", "consumption", "analyze", "analysis",
                "usage", "consumed", "consumption", "building_energy_analysis"
            ],
            "appliance_energy_breakdown": [
                "appliance", "breakdown", "by type", "hvac", "lighting",
                "computers", "equipment", "appliance_energy_breakdown"
            ],
            "peak_load_forecasting": [
                "forecast", "predict", "peak", "load", "future", "tomorrow",
                "next week", "demand", "peak_load_forecasting"
            ],
            "energy_saving_recommendations": [
                "recommend", "saving", "save", "efficiency", "optimize",
                "reduce", "suggestions", "tips", "energy_saving_recommendations"
            ],
            "solar_energy_estimation": [
                "solar", "renewable", "generation", "panel", "pv", "photovoltaic",
                "solar_energy_estimation"
            ],
            "cost_estimation": [
                "cost", "price", "bill", "expense", "money", "dollar", "usd",
                "cost_estimation"
            ]
        }
        
        # Find all matching capabilities
        matched_capabilities = []
        
        for capability, keywords in capability_keywords.items():
            # Check if capability name is explicitly mentioned
            if capability in prompt_lower or capability.replace("_", " ") in prompt_lower:
                matched_capabilities.append(capability)
            else:
                # Check for keyword matches
                matches = sum(1 for keyword in keywords if keyword in prompt_lower)
                if matches > 0:
                    matched_capabilities.append(capability)
        
        # Remove duplicates while preserving order
        matched_capabilities = list(dict.fromkeys(matched_capabilities))
        
        if not matched_capabilities:
            return None
        
        # Find agent with these capabilities
        for agent_name, agent in self.registry.items():
            # Check if agent has all requested capabilities
            agent_capabilities = [cap for cap in matched_capabilities if cap in agent.capabilities]
            if agent_capabilities:
                if len(agent_capabilities) == 1:
                    return {
                        "agent_name": agent_name,
                        "capability": agent_capabilities[0],
                        "agent": agent
                    }
                else:
                    return {
                        "agent_name": agent_name,
                        "capabilities": agent_capabilities,
                        "agent": agent
                    }
        
        return None
    
    async def route_query(self, prompt: str, user_id: str) -> Dict[str, Any]:
        """
        Route a natural language query to appropriate agent.
        Can handle multiple capabilities in a single query.
        
        Args:
            prompt: Natural language query
            user_id: User identifier
            
        Returns:
            Dictionary with agent response(s)
        """
        # Detect intent
        intent = self.detect_intent(prompt)
        
        if intent is None:
            return {
                "error": "No agent found to handle this query",
                "suggestions": [
                    "Try asking about building energy analysis",
                    "Request energy saving recommendations",
                    "Ask for peak load forecasting"
                ]
            }
        
        agent = intent["agent"]
        
        # Check if multiple capabilities requested
        if "capabilities" in intent:
            capabilities = intent["capabilities"]
            # Execute all capabilities and combine results
            results = {}
            all_responses = []
            
            for capability in capabilities:
                # Extract parameters for this capability
                parameters = self._extract_parameters(prompt, capability)
                
                # Create task assignment
                task_assignment = create_task_assignment(
                    sender="SupervisorAgent_Main",
                    recipient=agent.name,
                    task_name=capability,
                    parameters=parameters,
                    priority=2
                )
                
                # Send to agent
                try:
                    # Ensure URL is normalized
                    agent_url = normalize_url(agent.base_url)
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{agent_url}/task/sync",
                            json=task_assignment.dict()
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            results[capability] = result
                            all_responses.append({
                                "capability": capability,
                                "status": result.get("status", "SUCCESS"),
                                "data": result.get("results", {}).get("data", {}),
                                "explainability": result.get("results", {}).get("explainability", [])
                            })
                        else:
                            results[capability] = {
                                "error": f"Agent returned error: {response.status_code}",
                                "details": response.text
                            }
                            all_responses.append({
                                "capability": capability,
                                "status": "FAILURE",
                                "error": f"HTTP {response.status_code}"
                            })
                            
                except httpx.TimeoutException:
                    results[capability] = {"error": "Agent request timed out"}
                    all_responses.append({
                        "capability": capability,
                        "status": "FAILURE",
                        "error": "Request timed out"
                    })
                except Exception as e:
                    self.logger.error(f"Query routing failed for {capability}: {e}", exc_info=True)
                    results[capability] = {"error": str(e)}
                    all_responses.append({
                        "capability": capability,
                        "status": "FAILURE",
                        "error": str(e)
                    })
            
            # Update last_seen
            agent.last_seen = iso_now()
            self._save_registry()
            
            return {
                "agent": agent.name,
                "capabilities": capabilities,
                "responses": all_responses,
                "results": results,
                "summary": {
                    "total_requested": len(capabilities),
                    "successful": sum(1 for r in all_responses if r.get("status") == "SUCCESS"),
                    "failed": sum(1 for r in all_responses if r.get("status") == "FAILURE")
                }
            }
        
        else:
            # Single capability (original behavior)
            capability = intent["capability"]
            
            # Extract parameters from prompt (simple extraction)
            parameters = self._extract_parameters(prompt, capability)
            
            # Create task assignment
            task_assignment = create_task_assignment(
                sender="SupervisorAgent_Main",
                recipient=agent.name,
                task_name=capability,
                parameters=parameters,
                priority=2
            )
            
            # Send to agent
            try:
                # Ensure URL is normalized
                agent_url = normalize_url(agent.base_url)
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{agent_url}/task/sync",
                        json=task_assignment.dict()
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Update last_seen
                        agent.last_seen = iso_now()
                        self._save_registry()
                        
                        return {
                            "agent": agent.name,
                            "capability": capability,
                            "response": result
                        }
                    else:
                        return {
                            "error": f"Agent returned error: {response.status_code}",
                            "details": response.text
                        }
                        
            except httpx.TimeoutException:
                return {
                    "error": "Agent request timed out",
                    "agent_url": agent.base_url,
                    "suggestion": "Check if the agent is running and accessible"
                }
            except httpx.ConnectError as e:
                self.logger.error(f"Query routing failed: {e}", exc_info=True)
                return {
                    "error": f"Could not connect to agent at {agent.base_url}",
                    "agent_url": agent.base_url,
                    "suggestion": "Verify the agent URL is correct. If using Railway, ensure the agent is deployed and the URL uses the Railway domain (not localhost)"
                }
            except Exception as e:
                self.logger.error(f"Query routing failed: {e}", exc_info=True)
                return {
                    "error": str(e),
                    "agent_url": agent.base_url
                }
    
    def _extract_parameters(self, prompt: str, capability: str) -> Dict[str, Any]:
        """
        Extract task parameters from natural language prompt.
        
        Args:
            prompt: Natural language query
            capability: Detected capability
            
        Returns:
            Dictionary of parameters
        """
        prompt_lower = prompt.lower()
        parameters = {}
        
        # Extract building ID
        for building in ["building-a", "building-b", "building-c", "building a", "building b", "building c"]:
            if building in prompt_lower:
                parameters["building_id"] = building.replace(" ", "-").title()
                break
        
        if "building_id" not in parameters:
            parameters["building_id"] = "Building-A"  # Default
        
        # Extract date
        if "today" in prompt_lower:
            parameters["date"] = "today"
        elif "yesterday" in prompt_lower:
            parameters["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "tomorrow" in prompt_lower:
            parameters["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Extract forecast hours
        if "forecast" in prompt_lower or "predict" in prompt_lower:
            if "24" in prompt or "day" in prompt_lower:
                parameters["forecast_hours"] = 24
            elif "week" in prompt_lower:
                parameters["forecast_hours"] = 168  # 7 days
            else:
                parameters["forecast_hours"] = 24
        
        # Extract solar panel capacity
        if "solar" in prompt_lower:
            # Try to extract number
            import re
            numbers = re.findall(r'\d+', prompt)
            if numbers:
                parameters["panel_capacity_kw"] = float(numbers[0])
            else:
                parameters["panel_capacity_kw"] = 100.0
        
        return parameters
    
    async def check_agent_health(self, agent: AgentMetadata) -> Dict[str, Any]:
        """
        Check health status of an agent.
        
        Args:
            agent: Agent metadata
            
        Returns:
            Dictionary with health status
        """
        try:
            # Ensure URL is normalized
            health_url = normalize_url(agent.health_url)
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = datetime.now()
                response = await client.get(health_url)
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "name": agent.name,
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "details": data
                    }
                else:
                    return {
                        "name": agent.name,
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "error": f"HTTP {response.status_code}"
                    }
        except httpx.TimeoutException:
            return {
                "name": agent.name,
                "status": "timeout",
                "response_time_ms": None,
                "error": "Request timed out"
            }
        except Exception as e:
            return {
                "name": agent.name,
                "status": "error",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def aggregate_health(self) -> Dict[str, Any]:
        """
        Check health of all registered agents.
        
        Returns:
            Dictionary with aggregate health status
        """
        import asyncio
        
        agents = list(self.registry.values())
        health_checks = await asyncio.gather(
            *[self.check_agent_health(agent) for agent in agents],
            return_exceptions=True
        )
        
        results = []
        for check in health_checks:
            if isinstance(check, Exception):
                results.append({
                    "status": "error",
                    "error": str(check)
                })
            else:
                results.append(check)
        
        healthy_count = sum(1 for r in results if r.get("status") == "healthy")
        
        return {
            "supervisor_status": "ok",
            "agents": results,
            "total_agents": len(agents),
            "healthy_agents": healthy_count
        }

