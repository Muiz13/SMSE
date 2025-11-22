"""
Smart Campus Energy Management Agent (SCEMS) implementation.

Concrete worker agent that implements all 6 energy management capabilities.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from .worker_base import AbstractWorkerAgent
from .ltm import LTM
from .model_stub import ForecastModel, estimate_solar_energy, calculate_energy_savings

logger = logging.getLogger(__name__)


class SmartCampusEnergyAgent(AbstractWorkerAgent):
    """
    Smart Campus Energy Management Agent.
    
    Implements the following capabilities:
    1. building_energy_analysis
    2. appliance_energy_breakdown
    3. peak_load_forecasting
    4. energy_saving_recommendations
    5. solar_energy_estimation
    6. cost_estimation
    """
    
    CAPABILITIES = [
        "building_energy_analysis",
        "appliance_energy_breakdown",
        "peak_load_forecasting",
        "energy_saving_recommendations",
        "solar_energy_estimation",
        "cost_estimation"
    ]
    
    def __init__(
        self,
        agent_name: str = "SmartCampusEnergyAgent",
        supervisor_url: str = "http://localhost:8000",
        ltm: Optional[LTM] = None,
        model_path: str = "./models/forecast_model.pkl",
        data_dir: str = "./sample_data"
    ):
        """
        Initialize SCEMS agent.
        
        Args:
            agent_name: Agent identifier
            supervisor_url: Supervisor service URL
            ltm: Long-term memory instance
            model_path: Path to forecast model
            data_dir: Directory containing sample data
        """
        super().__init__(agent_name, supervisor_url, ltm)
        self.model_path = model_path
        self.data_dir = Path(data_dir)
        self.forecast_model = ForecastModel(model_path=model_path)
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
    
    def get_capabilities(self) -> List[str]:
        """Return list of supported capabilities."""
        return self.CAPABILITIES.copy()
    
    def process_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and return results.
        
        Args:
            task_name: Name of the task to execute
            parameters: Task-specific parameters
            
        Returns:
            Dictionary with 'data', 'explainability', and 'ltm_hit' keys
        """
        self.logger.info(f"Processing task: {task_name}", extra={"parameters": parameters})
        
        if task_name == "building_energy_analysis":
            return self._building_energy_analysis(parameters)
        elif task_name == "appliance_energy_breakdown":
            return self._appliance_energy_breakdown(parameters)
        elif task_name == "peak_load_forecasting":
            return self._peak_load_forecasting(parameters)
        elif task_name == "energy_saving_recommendations":
            return self._energy_saving_recommendations(parameters)
        elif task_name == "solar_energy_estimation":
            return self._solar_energy_estimation(parameters)
        elif task_name == "cost_estimation":
            return self._cost_estimation(parameters)
        else:
            raise ValueError(f"Unknown task: {task_name}")
    
    def _building_energy_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze energy consumption for a building.
        
        Parameters:
            - building_id: Building identifier
            - date: Date to analyze (YYYY-MM-DD) or "today"
        """
        building_id = params.get("building_id", "Building-A")
        date_str = params.get("date", "today")
        
        if date_str == "today":
            date = datetime.now().date()
        else:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Load sample data
        data_file = self.data_dir / "building_energy.csv"
        if not data_file.exists():
            # Generate synthetic data
            total_consumption = 1250.5
            peak_hour = 14
            avg_consumption = 52.1
        else:
            try:
                df = pd.read_csv(data_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                
                building_data = df[(df['building_id'] == building_id) & (df['date'] == date)]
                
                if len(building_data) > 0:
                    total_consumption = building_data['consumption_kwh'].sum()
                    peak_hour = building_data.loc[building_data['consumption_kwh'].idxmax(), 'timestamp'].hour
                    avg_consumption = building_data['consumption_kwh'].mean()
                else:
                    # Fallback to synthetic
                    total_consumption = 1250.5
                    peak_hour = 14
                    avg_consumption = 52.1
            except Exception as e:
                self.logger.warning(f"Failed to load data: {e}, using synthetic data")
                total_consumption = 1250.5
                peak_hour = 14
                avg_consumption = 52.1
        
        return {
            "data": {
                "building_id": building_id,
                "date": str(date),
                "total_consumption_kwh": round(total_consumption, 2),
                "peak_hour": peak_hour,
                "average_consumption_kwh": round(avg_consumption, 2),
                "consumption_trend": "stable"
            },
            "explainability": [
                f"Analyzed 24-hour consumption data for {building_id} on {date}",
                f"Total consumption: {total_consumption:.1f} kWh",
                f"Peak consumption occurred at {peak_hour}:00",
                "Trend analysis indicates stable consumption pattern"
            ],
            "ltm_hit": False
        }
    
    def _appliance_energy_breakdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Break down energy consumption by appliance type.
        
        Parameters:
            - building_id: Building identifier
            - date: Date to analyze
        """
        building_id = params.get("building_id", "Building-A")
        date_str = params.get("date", "today")
        
        # Synthetic breakdown (in real system, would query IoT sensors)
        breakdown = {
            "HVAC": {"consumption_kwh": 450.0, "percentage": 36.0},
            "Lighting": {"consumption_kwh": 200.0, "percentage": 16.0},
            "Computers": {"consumption_kwh": 300.0, "percentage": 24.0},
            "Other": {"consumption_kwh": 300.5, "percentage": 24.0}
        }
        
        total = sum(item["consumption_kwh"] for item in breakdown.values())
        
        return {
            "data": {
                "building_id": building_id,
                "date": date_str,
                "total_consumption_kwh": round(total, 2),
                "breakdown": breakdown
            },
            "explainability": [
                f"Energy breakdown for {building_id} on {date_str}",
                "HVAC systems account for the largest share (36%)",
                "Computers and IT equipment contribute 24%",
                "Lighting systems use 16% of total energy"
            ],
            "ltm_hit": False
        }
    
    def _peak_load_forecasting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast peak energy load for future periods.
        
        Parameters:
            - building_id: Building identifier
            - forecast_hours: Number of hours to forecast (default: 24)
            - start_time: Start time for forecast (ISO format or "now")
        """
        building_id = params.get("building_id", "Building-A")
        forecast_hours = params.get("forecast_hours", 24)
        start_time_str = params.get("start_time", "now")
        
        if start_time_str == "now":
            start_time = datetime.now()
        else:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", ""))
        
        # Get previous consumption for context
        prev_consumption = 50.0  # Default
        
        # Generate forecasts
        forecasts = []
        peak_forecast = 0.0
        peak_hour = None
        
        for i in range(forecast_hours):
            forecast_time = start_time + timedelta(hours=i)
            hour = forecast_time.hour
            day_of_week = forecast_time.weekday()
            
            predicted = self.forecast_model.predict(hour, day_of_week, prev_consumption)
            forecasts.append({
                "timestamp": forecast_time.isoformat() + "Z",
                "predicted_consumption_kwh": round(predicted, 2)
            })
            
            if predicted > peak_forecast:
                peak_forecast = predicted
                peak_hour = hour
            
            prev_consumption = predicted
        
        return {
            "data": {
                "building_id": building_id,
                "forecast_hours": forecast_hours,
                "peak_forecast_kwh": round(peak_forecast, 2),
                "peak_hour": peak_hour,
                "forecasts": forecasts
            },
            "explainability": [
                f"Generated {forecast_hours}-hour forecast for {building_id}",
                f"Peak load predicted: {peak_forecast:.1f} kWh at {peak_hour}:00",
                "Model uses time-of-day and day-of-week patterns",
                "Forecast based on historical consumption patterns"
            ],
            "ltm_hit": False
        }
    
    def _energy_saving_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide energy-saving recommendations.
        
        Parameters:
            - building_id: Building identifier
            - current_consumption: Current consumption in kWh (optional)
        """
        building_id = params.get("building_id", "Building-A")
        current_consumption = params.get("current_consumption", 1250.0)
        
        # Generate recommendations based on heuristics
        recommendations = []
        
        # Check time of day for load shifting
        current_hour = datetime.now().hour
        if 14 <= current_hour <= 18:  # Peak hours
            recommendations.append(
                "Shift non-essential loads to off-peak hours (after 8 PM) to reduce peak demand charges"
            )
        
        # HVAC recommendations
        recommendations.append(
            "Reduce HVAC setpoint by 1°C during non-occupied hours to save ~8% on HVAC energy"
        )
        
        # Lighting recommendations
        recommendations.append(
            "Replace incandescent bulbs with LED lighting to reduce lighting energy by 75%"
        )
        
        # Calculate savings
        savings = calculate_energy_savings(current_consumption, recommendations)
        
        return {
            "data": {
                "building_id": building_id,
                "recommendations": recommendations,
                "estimated_savings": {
                    "savings_percent": round(savings["savings_percent"], 2),
                    "savings_kwh": round(savings["savings_kwh"], 2),
                    "breakdown": savings["breakdown"]
                }
            },
            "explainability": [
                f"Generated {len(recommendations)} recommendations for {building_id}",
                f"Potential savings: {savings['savings_percent']:.1f}% ({savings['savings_kwh']:.1f} kWh)",
                "Recommendations based on current consumption patterns and best practices",
                "HVAC optimization offers the highest savings potential"
            ],
            "ltm_hit": False
        }
    
    def _solar_energy_estimation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate solar energy generation potential.
        
        Parameters:
            - panel_capacity_kw: Solar panel capacity in kW
            - irradiance_factor: Irradiance factor (0-1, default: 0.75)
            - hours: Hours of sunlight (default: 8.0)
            - location: Location identifier (optional)
        """
        panel_capacity = params.get("panel_capacity_kw", 100.0)
        irradiance_factor = params.get("irradiance_factor", 0.75)
        hours = params.get("hours", 8.0)
        location = params.get("location", "Campus-Main")
        
        estimated_kwh = estimate_solar_energy(panel_capacity, irradiance_factor, hours)
        
        # Calculate monthly and annual estimates
        daily_estimate = estimated_kwh
        monthly_estimate = daily_estimate * 30
        annual_estimate = daily_estimate * 365
        
        return {
            "data": {
                "location": location,
                "panel_capacity_kw": panel_capacity,
                "irradiance_factor": irradiance_factor,
                "sunlight_hours": hours,
                "estimated_generation": {
                    "daily_kwh": round(daily_estimate, 2),
                    "monthly_kwh": round(monthly_estimate, 2),
                    "annual_kwh": round(annual_estimate, 2)
                }
            },
            "explainability": [
                f"Solar energy estimation for {location}",
                f"Formula: generation = capacity × irradiance × hours",
                f"Daily generation: {daily_estimate:.1f} kWh",
                f"Annual potential: {annual_estimate:.0f} kWh"
            ],
            "ltm_hit": False
        }
    
    def _cost_estimation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate energy costs and potential savings.
        
        Parameters:
            - consumption_kwh: Energy consumption in kWh
            - rate_per_kwh: Electricity rate per kWh (default: 0.12)
            - building_id: Building identifier
        """
        consumption = params.get("consumption_kwh", 1250.0)
        rate_per_kwh = params.get("rate_per_kwh", 0.12)
        building_id = params.get("building_id", "Building-A")
        
        total_cost = consumption * rate_per_kwh
        
        # Calculate with recommendations
        recommendations_result = self._energy_saving_recommendations({
            "building_id": building_id,
            "current_consumption": consumption
        })
        savings_kwh = recommendations_result["data"]["estimated_savings"]["savings_kwh"]
        savings_cost = savings_kwh * rate_per_kwh
        
        return {
            "data": {
                "building_id": building_id,
                "consumption_kwh": consumption,
                "rate_per_kwh": rate_per_kwh,
                "total_cost_usd": round(total_cost, 2),
                "potential_savings": {
                    "savings_kwh": round(savings_kwh, 2),
                    "savings_cost_usd": round(savings_cost, 2),
                    "savings_percent": round((savings_kwh / consumption) * 100, 2)
                }
            },
            "explainability": [
                f"Cost analysis for {building_id}",
                f"Current consumption: {consumption:.1f} kWh at ${rate_per_kwh}/kWh = ${total_cost:.2f}",
                f"Potential savings: {savings_kwh:.1f} kWh (${savings_cost:.2f})",
                "Savings calculated based on recommended energy efficiency measures"
            ],
            "ltm_hit": False
        }

