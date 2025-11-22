"""
Synthetic IoT data generator for building energy consumption.

Generates realistic time-series data with occupancy patterns and anomalies.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_building_energy_data(
    building_id: str,
    start_date: datetime,
    days: int = 30,
    base_load: float = 50.0,
    peak_multiplier: float = 1.5
) -> pd.DataFrame:
    """
    Generate synthetic energy consumption data for a building.
    
    Args:
        building_id: Building identifier
        start_date: Start date for data generation
        days: Number of days to generate
        base_load: Base energy load in kWh
        peak_multiplier: Multiplier for peak hours
        
    Returns:
        DataFrame with columns: timestamp, building_id, consumption_kwh
    """
    timestamps = []
    consumptions = []
    
    current_date = start_date
    
    for day in range(days):
        day_of_week = current_date.weekday()
        
        # Weekend has lower base consumption
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        
        for hour in range(24):
            for minute in [0, 15, 30, 45]:  # 4 readings per hour
                timestamp = current_date.replace(
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0
                )
                
                # Base consumption with time-of-day pattern
                hour_factor = 1.0
                if 6 <= hour <= 22:  # Daytime hours
                    hour_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 16)
                else:  # Nighttime
                    hour_factor = 0.6
                
                # Peak hours (2 PM - 6 PM)
                if 14 <= hour <= 18:
                    hour_factor *= peak_multiplier
                
                # Add some randomness
                noise = np.random.normal(0, 0.1)
                
                # Occasional anomalies (5% chance)
                anomaly = 1.0
                if np.random.random() < 0.05:
                    anomaly = np.random.uniform(1.2, 2.0)  # Spike
                
                consumption = base_load * weekend_factor * hour_factor * (1 + noise) * anomaly
                consumption = max(10.0, consumption)  # Minimum 10 kWh
                
                timestamps.append(timestamp)
                consumptions.append(round(consumption, 2))
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "building_id": building_id,
        "consumption_kwh": consumptions
    })
    
    return df


def generate_all_buildings(
    output_dir: str = "./sample_data",
    days: int = 30
) -> None:
    """
    Generate data for all buildings.
    
    Args:
        output_dir: Output directory for CSV files
        days: Number of days to generate
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    buildings = ["Building-A", "Building-B", "Building-C"]
    start_date = datetime.now() - timedelta(days=days)
    
    all_data = []
    
    for building_id in buildings:
        logger.info(f"Generating data for {building_id}...")
        
        # Vary base load per building
        base_loads = {"Building-A": 50.0, "Building-B": 75.0, "Building-C": 60.0}
        base_load = base_loads.get(building_id, 50.0)
        
        df = generate_building_energy_data(
            building_id=building_id,
            start_date=start_date,
            days=days,
            base_load=base_load
        )
        
        all_data.append(df)
    
    # Combine all buildings
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values("timestamp")
    
    # Save combined file
    output_file = output_path / "building_energy.csv"
    combined_df.to_csv(output_file, index=False)
    logger.info(f"Saved combined data to {output_file} ({len(combined_df)} rows)")
    
    # Save individual building files
    for building_id in buildings:
        building_df = combined_df[combined_df["building_id"] == building_id]
        building_file = output_path / f"{building_id.lower().replace('-', '_')}_energy.csv"
        building_df.to_csv(building_file, index=False)
        logger.info(f"Saved {building_id} data to {building_file} ({len(building_df)} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic building energy data")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./sample_data",
        help="Output directory for CSV files"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of data to generate"
    )
    
    args = parser.parse_args()
    
    generate_all_buildings(output_dir=args.output_dir, days=args.days)
    print(f"\nData generation complete! Files saved to {args.output_dir}")

