from typing import Tuple
import numpy as np
import pandas as pd
from src.config import UTILIZATION_BINS, UTILIZATION_LABELS


def compute_vehicle_utilization(vehicle_summary: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Phase 4: Fleet Utilization Analysis.
    Classifies vehicle utilization into High (>80%), Moderate (50%-80%), and Low (<50%) bands
    using both distance travelled and completed trip count methodologies.
    """
    df = vehicle_summary.copy()

    # 1. By distance travelled
    max_dist = df["Total_Distance"].max()
    df["Utilization_Distance"] = df["Total_Distance"] / max_dist if max_dist > 0 else 0.0
    df["Category_distance"] = pd.cut(
        df["Utilization_Distance"], bins=UTILIZATION_BINS, labels=UTILIZATION_LABELS
    )

    # 2. By trip count completed
    max_trips = df["TripCount"].max()
    df["Utilization_Trips"] = df["TripCount"] / max_trips if max_trips > 0 else 0.0
    df["Category_tripcount"] = pd.cut(
        df["Utilization_Trips"], bins=UTILIZATION_BINS, labels=UTILIZATION_LABELS
    )

    split_distance = df["Category_distance"].value_counts().reindex(UTILIZATION_LABELS, fill_value=0)
    split_trips = df["Category_tripcount"].value_counts().reindex(UTILIZATION_LABELS, fill_value=0)

    return df, split_distance, split_trips
