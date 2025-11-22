"""
ML model stub for energy forecasting and optimization.

Provides lightweight machine learning models for peak load forecasting
and deterministic formulas for solar energy estimation.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ForecastModel:
    """
    Lightweight forecasting model for peak load prediction.
    
    Uses LinearRegression on time-series features:
    - Hour of day (0-23)
    - Day of week (0-6)
    - Previous consumption (rolling average)
    """
    
    def __init__(self, model_path: str = "./models/forecast_model.pkl"):
        """
        Initialize forecast model.
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = Path(model_path)
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Load model if exists
        if self.model_path.exists():
            try:
                self.load()
                logger.info(f"Loaded model from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, will train new model")
    
    def _extract_features(self, hour: int, day_of_week: int, prev_consumption: float) -> np.ndarray:
        """
        Extract features from time and consumption data.
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            prev_consumption: Previous consumption value
            
        Returns:
            Feature array
        """
        # Cyclical encoding for hour and day
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        return np.array([hour_sin, hour_cos, day_sin, day_cos, prev_consumption])
    
    def train(self, data_path: str) -> None:
        """
        Train the model on historical data.
        
        Args:
            data_path: Path to CSV file with columns: timestamp, building_id, consumption_kwh
        """
        try:
            df = pd.read_csv(data_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Calculate rolling average of previous consumption
            df = df.sort_values('timestamp')
            df['prev_consumption'] = df.groupby('building_id')['consumption_kwh'].shift(1).fillna(df['consumption_kwh'].mean())
            
            # Extract features
            X = []
            y = []
            
            for _, row in df.iterrows():
                features = self._extract_features(
                    row['hour'],
                    row['day_of_week'],
                    row['prev_consumption']
                )
                X.append(features)
                y.append(row['consumption_kwh'])
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model
            self.save()
            
            logger.info(f"Model trained on {len(X)} samples, R² score: {self.model.score(X_scaled, y):.3f}")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}", exc_info=True)
            raise
    
    def predict(self, hour: int, day_of_week: int, prev_consumption: float) -> float:
        """
        Predict consumption for given time and previous consumption.
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0-6)
            prev_consumption: Previous consumption value
            
        Returns:
            Predicted consumption in kWh
        """
        if not self.is_trained:
            # Fallback: simple heuristic
            base_load = 50.0  # Base load in kWh
            hour_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 24)  # Peak around afternoon
            return base_load * hour_factor
        
        features = self._extract_features(hour, day_of_week, prev_consumption)
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        
        return max(0.0, prediction)  # Ensure non-negative
    
    def save(self) -> None:
        """Save model to disk."""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'is_trained': self.is_trained
                }, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}", exc_info=True)
    
    def load(self) -> None:
        """Load model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = data.get('is_trained', False)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise


def estimate_solar_energy(
    panel_capacity_kw: float,
    irradiance_factor: float = 0.75,
    hours: float = 8.0
) -> float:
    """
    Estimate solar energy generation using deterministic formula.
    
    Formula: est_kw = panel_capacity_kw * irradiance_factor * hours
    
    Args:
        panel_capacity_kw: Solar panel capacity in kW
        irradiance_factor: Irradiance factor (0-1), default 0.75
        hours: Hours of sunlight, default 8.0
        
    Returns:
        Estimated energy generation in kWh
    """
    return panel_capacity_kw * irradiance_factor * hours


def calculate_energy_savings(
    current_consumption: float,
    recommendations: list[str]
) -> Dict[str, Any]:
    """
    Calculate estimated energy savings from recommendations.
    
    Args:
        current_consumption: Current energy consumption in kWh
        recommendations: List of recommendation strings
        
    Returns:
        Dictionary with savings estimates
    """
    total_savings_percent = 0.0
    savings_breakdown = {}
    
    for rec in recommendations:
        if "shift" in rec.lower() or "off-peak" in rec.lower():
            savings_percent = 0.05  # 5% savings from load shifting
            total_savings_percent += savings_percent
            savings_breakdown["load_shifting"] = savings_percent
        elif "hvac" in rec.lower() or "setpoint" in rec.lower():
            savings_percent = 0.08  # 8% savings from HVAC optimization
            total_savings_percent += savings_percent
            savings_breakdown["hvac_optimization"] = savings_percent
        elif "lighting" in rec.lower():
            savings_percent = 0.03  # 3% savings from lighting optimization
            total_savings_percent += savings_percent
            savings_breakdown["lighting"] = savings_percent
    
    # Cap total savings at 20%
    total_savings_percent = min(total_savings_percent, 0.20)
    
    estimated_savings_kwh = current_consumption * total_savings_percent
    
    return {
        "savings_percent": total_savings_percent * 100,
        "savings_kwh": estimated_savings_kwh,
        "breakdown": savings_breakdown
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--train":
        # Train model
        data_path = sys.argv[2] if len(sys.argv) > 2 else "./sample_data/building_energy.csv"
        model_path = sys.argv[3] if len(sys.argv) > 3 else "./models/forecast_model.pkl"
        
        model = ForecastModel(model_path=model_path)
        model.train(data_path)
        print(f"Model trained and saved to {model_path}")
    else:
        print("Usage: python model_stub.py --train [data_path] [model_path]")

