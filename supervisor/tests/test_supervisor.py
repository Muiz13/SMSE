"""
Tests for Supervisor agent.
"""

import pytest
import os
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supervisor import Supervisor
from schemas import RegisterRequest


@pytest.fixture
def supervisor():
    """Create a test supervisor instance."""
    test_registry = "./test_registry.json"
    sup = Supervisor(registry_path=test_registry)
    yield sup
    # Cleanup
    if Path(test_registry).exists():
        os.remove(test_registry)


def test_register_agent(supervisor):
    """Test agent registration."""
    request = RegisterRequest(
        name="TestAgent",
        base_url="http://localhost:8002",
        health_url="http://localhost:8002/health",
        capabilities=["capability1", "capability2"]
    )
    
    success = supervisor.register_agent(request)
    assert success == True
    
    agents = supervisor.get_registry()
    assert len(agents) == 1
    assert agents[0].name == "TestAgent"


def test_detect_intent(supervisor):
    """Test intent detection from natural language."""
    # Register an agent first
    request = RegisterRequest(
        name="TestAgent",
        base_url="http://localhost:8002",
        health_url="http://localhost:8002/health",
        capabilities=["building_energy_analysis"]
    )
    supervisor.register_agent(request)
    
    # Test intent detection
    intent = supervisor.detect_intent("Analyze energy consumption for Building A")
    assert intent is not None
    assert intent["capability"] == "building_energy_analysis"
    assert intent["agent_name"] == "TestAgent"


def test_detect_intent_no_match(supervisor):
    """Test intent detection with no matching capability."""
    intent = supervisor.detect_intent("What is the weather today?")
    assert intent is None


def test_extract_parameters(supervisor):
    """Test parameter extraction from prompt."""
    prompt = "Analyze energy consumption for Building A today"
    parameters = supervisor._extract_parameters(prompt, "building_energy_analysis")
    
    assert "building_id" in parameters
    assert parameters["building_id"] == "Building-A"


def test_get_registry(supervisor):
    """Test registry retrieval."""
    # Register multiple agents
    for i in range(3):
        request = RegisterRequest(
            name=f"Agent{i}",
            base_url=f"http://localhost:800{i+2}",
            health_url=f"http://localhost:800{i+2}/health",
            capabilities=["capability1"]
        )
        supervisor.register_agent(request)
    
    agents = supervisor.get_registry()
    assert len(agents) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

