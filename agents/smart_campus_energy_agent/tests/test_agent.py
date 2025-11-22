"""
Tests for Smart Campus Energy Agent.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SmartCampusEnergyAgent
from ltm import LTM
from shared.protocol import TaskAssignment, create_task_assignment


@pytest.fixture
def agent():
    """Create a test agent instance."""
    ltm = LTM(backend_type="file", path="./test_ltm.json")
    return SmartCampusEnergyAgent(
        agent_name="TestAgent",
        supervisor_url="http://localhost:8000",
        ltm=ltm
    )


def test_get_capabilities(agent):
    """Test capability listing."""
    capabilities = agent.get_capabilities()
    assert len(capabilities) == 6
    assert "building_energy_analysis" in capabilities
    assert "peak_load_forecasting" in capabilities


def test_building_energy_analysis(agent):
    """Test building energy analysis capability."""
    result = agent.process_task(
        "building_energy_analysis",
        {"building_id": "Building-A", "date": "today"}
    )
    
    assert "data" in result
    assert "explainability" in result
    assert "ltm_hit" in result
    assert result["data"]["building_id"] == "Building-A"
    assert "total_consumption_kwh" in result["data"]


def test_appliance_energy_breakdown(agent):
    """Test appliance energy breakdown capability."""
    result = agent.process_task(
        "appliance_energy_breakdown",
        {"building_id": "Building-A", "date": "today"}
    )
    
    assert "data" in result
    assert "breakdown" in result["data"]
    assert "HVAC" in result["data"]["breakdown"]


def test_peak_load_forecasting(agent):
    """Test peak load forecasting capability."""
    result = agent.process_task(
        "peak_load_forecasting",
        {"building_id": "Building-A", "forecast_hours": 24}
    )
    
    assert "data" in result
    assert "peak_forecast_kwh" in result["data"]
    assert "forecasts" in result["data"]
    assert len(result["data"]["forecasts"]) == 24


def test_energy_saving_recommendations(agent):
    """Test energy saving recommendations capability."""
    result = agent.process_task(
        "energy_saving_recommendations",
        {"building_id": "Building-A", "current_consumption": 1000.0}
    )
    
    assert "data" in result
    assert "recommendations" in result["data"]
    assert len(result["data"]["recommendations"]) > 0
    assert "estimated_savings" in result["data"]


def test_solar_energy_estimation(agent):
    """Test solar energy estimation capability."""
    result = agent.process_task(
        "solar_energy_estimation",
        {"panel_capacity_kw": 100.0, "irradiance_factor": 0.75, "hours": 8.0}
    )
    
    assert "data" in result
    assert "estimated_generation" in result["data"]
    assert result["data"]["estimated_generation"]["daily_kwh"] > 0


def test_cost_estimation(agent):
    """Test cost estimation capability."""
    result = agent.process_task(
        "cost_estimation",
        {"consumption_kwh": 1000.0, "rate_per_kwh": 0.12}
    )
    
    assert "data" in result
    assert "total_cost_usd" in result["data"]
    assert result["data"]["total_cost_usd"] == 120.0


def test_handle_task_assignment(agent):
    """Test task assignment handling."""
    assignment = create_task_assignment(
        sender="SupervisorAgent_Main",
        recipient="TestAgent",
        task_name="building_energy_analysis",
        parameters={"building_id": "Building-A", "date": "today"}
    )
    
    report = agent.handle_task_assignment(assignment)
    
    assert report.status == "SUCCESS"
    assert report.related_message_id == assignment.message_id
    assert "results" in report.dict()


def test_unknown_task(agent):
    """Test handling of unknown task."""
    with pytest.raises(ValueError, match="Unknown task"):
        agent.process_task("unknown_task", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

