"""
Data Preprocessing and Ingestion Module.
Handles loading raw shift and trip logs, parsing timestamps, cleaning,
and aggregating driver & vehicle operational metrics.
"""

from dataclasses import dataclass
import os
from typing import Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class DatasetSummary:
    total_records: int
    num_drivers: int
    num_vehicles: int
    num_stations: int
    avg_shift_distance: float
    avg_shift_duration: float
    workload_variance: float


class DataIngestionPipeline:
    """Ingests raw shift logs and computes operational profiles for drivers and vehicles."""

    def __init__(self, shift_file: str = "data/raw/ShiftData.csv", trip_file: Optional[str] = None):
        # Fallback to current directory if not found in data/raw
        if not os.path.exists(shift_file) and os.path.exists("ShiftData.csv"):
            shift_file = "ShiftData.csv"
        if trip_file and not os.path.exists(trip_file) and os.path.exists("TripData.csv"):
            trip_file = "TripData.csv"

        self.shift_file = shift_file
        self.trip_file = trip_file
        self.raw_shifts: Optional[pd.DataFrame] = None
        self.raw_trips: Optional[pd.DataFrame] = None
        self.cleaned_shifts: Optional[pd.DataFrame] = None
        self.driver_profiles: Optional[pd.DataFrame] = None
        self.vehicle_profiles: Optional[pd.DataFrame] = None

    def load_data(self) -> pd.DataFrame:
        """Loads and cleans raw shift records."""
        if not os.path.exists(self.shift_file):
            raise FileNotFoundError(f"Shift log dataset '{self.shift_file}' not found.")

        df = pd.read_csv(self.shift_file)
        # Drop redundant unnamed trailing columns if present
        unnamed_cols = [c for c in df.columns if c.startswith("Unnamed")]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # Parse start and end times
        df['StartTime_dt'] = pd.to_datetime(df['StartTime'], format='%H:%M:%S', errors='coerce')
        df['EndTime_dt'] = pd.to_datetime(df['EndTime'], format='%H:%M:%S', errors='coerce')

        # Shift duration in hours
        df['Duration_Hours'] = (df['EndTime_dt'] - df['StartTime_dt']).dt.total_seconds() / 3600.0

        # Handle any overnight or invalid shifts if duration is negative
        df['Duration_Hours'] = df['Duration_Hours'].apply(lambda d: d + 24.0 if d < 0 else d)

        # Fill missing distances or durations with column medians
        df['Distance'] = df['Distance'].fillna(df['Distance'].median())
        df['Duration_Hours'] = df['Duration_Hours'].fillna(df['Duration_Hours'].median())
        df['Total'] = df['Total'].fillna(df['Total'].median())

        self.raw_shifts = df
        self.cleaned_shifts = df
        return df

    def aggregate_profiles(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Aggregates metrics for each unique pilot (driver) and vehicle."""
        if self.cleaned_shifts is None:
            self.load_data()

        df = self.cleaned_shifts

        # Driver Profiles
        driver_stats = df.groupby('Pilotcode').agg(
            Avg_Distance=('Distance', 'mean'),
            Total_Distance=('Distance', 'sum'),
            Avg_Duration=('Duration_Hours', 'mean'),
            Total_Duration=('Duration_Hours', 'sum'),
            Shift_Count=('Distance', 'count'),
            Avg_Revenue=('Total', 'mean'),
            Total_Revenue=('Total', 'sum'),
            Primary_Station=('StationCode', lambda s: s.mode()[0])
        ).reset_index()

        # Vehicle Profiles
        vehicle_stats = df.groupby('VehicleCode').agg(
            Avg_Distance=('Distance', 'mean'),
            Total_Distance=('Distance', 'sum'),
            Avg_Duration=('Duration_Hours', 'mean'),
            Total_Duration=('Duration_Hours', 'sum'),
            Shift_Count=('Distance', 'count'),
            Avg_Revenue=('Total', 'mean'),
            Total_Revenue=('Total', 'sum'),
            Primary_Station=('StationCode', lambda s: s.mode()[0])
        ).reset_index()

        self.driver_profiles = driver_stats
        self.vehicle_profiles = vehicle_stats
        return driver_stats, vehicle_stats

    def get_summary(self) -> DatasetSummary:
        """Returns high-level statistics of the dataset."""
        if self.driver_profiles is None or self.vehicle_profiles is None:
            self.aggregate_profiles()

        df = self.cleaned_shifts
        dist_series = self.driver_profiles['Avg_Distance']

        return DatasetSummary(
            total_records=len(df),
            num_drivers=len(self.driver_profiles),
            num_vehicles=len(self.vehicle_profiles),
            num_stations=df['StationCode'].nunique(),
            avg_shift_distance=float(dist_series.mean()),
            avg_shift_duration=float(self.driver_profiles['Avg_Duration'].mean()),
            workload_variance=float(dist_series.var(ddof=0))
        )
