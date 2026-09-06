import pandas as pd


def summarize_drivers(shifts: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize driver profiles computing average distance (Di), average duration (Ti),
    total distance, shift counts, and home station assignment.
    """
    driver_summary = (
        shifts.groupby("Pilotcode")
        .agg(
            Avg_Distance=("Distance", "mean"),
            Avg_Duration=("Duration_Hours", "mean"),
            Total_Distance=("Distance", "sum"),
            Shift_Count=("Distance", "count"),
            StationCode=("StationCode", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
        )
        .reset_index()
    )
    return driver_summary


def summarize_vehicles(shifts: pd.DataFrame, trips: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize vehicle profiles computing average distance, duration, total distance,
    home station, and merging trip transaction counts.
    """
    trips_per_veh = trips.groupby("VehicleCode").size().rename("TripCount")

    vehicle_summary = (
        shifts.groupby("VehicleCode")
        .agg(
            Avg_Distance=("Distance", "mean"),
            Avg_Duration=("Duration_Hours", "mean"),
            Total_Distance=("Distance", "sum"),
            Shift_Count=("Distance", "count"),
            StationCode=("StationCode", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
        )
        .reset_index()
        .merge(trips_per_veh, on="VehicleCode", how="left")
    )

    vehicle_summary["TripCount"] = vehicle_summary["TripCount"].fillna(0).astype(int)
    return vehicle_summary
