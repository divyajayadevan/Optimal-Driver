from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

from src.config import (
    DEFAULT_SHIFT_FILE,
    FALLBACK_SHIFT_FILE,
    DEFAULT_TRIP_FILE,
    FALLBACK_TRIP_FILE,
)


def resolve_file_path(primary: Path, fallback: Path) -> Path:
    """Resolve file path between primary (data/raw) and fallback locations."""
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    raise FileNotFoundError(
        f"Could not locate dataset. Checked '{primary}' and '{fallback}'."
    )


def load_shift_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Phase 1: Ingest and validate historical shift logs (ShiftData.csv).
    Computes shift duration in hours (EndTime - StartTime).
    """
    path = file_path or resolve_file_path(DEFAULT_SHIFT_FILE, FALLBACK_SHIFT_FILE)
    shifts = pd.read_csv(path)

    # Required columns validation
    required_cols = {"Pilotcode", "VehicleCode", "StationCode", "StartTime", "EndTime", "Distance"}
    missing = required_cols - set(shifts.columns)
    if missing:
        raise ValueError(f"ShiftData is missing required columns: {missing}")

    # Standardize and parse timestamps
    shifts["StartTime_dt"] = pd.to_datetime(shifts["StartTime"], format="%H:%M:%S", errors="coerce")
    shifts["EndTime_dt"] = pd.to_datetime(shifts["EndTime"], format="%H:%M:%S", errors="coerce")
    shifts["Duration_Hours"] = (shifts["EndTime_dt"] - shifts["StartTime_dt"]).dt.total_seconds() / 3600.0

    return shifts


def load_trip_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Phase 1: Ingest granular ride transactions (TripData.csv).
    """
    path = file_path or resolve_file_path(DEFAULT_TRIP_FILE, FALLBACK_TRIP_FILE)
    trips = pd.read_csv(path)

    if "VehicleCode" not in trips.columns:
        raise ValueError("TripData must contain 'VehicleCode' column.")

    return trips
