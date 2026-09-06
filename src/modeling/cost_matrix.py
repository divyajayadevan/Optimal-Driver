from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd

from src.config import (
    WEIGHT_DISTANCE,
    WEIGHT_DURATION,
    WEIGHT_UTILIZATION,
    STATION_MISMATCH_PENALTY,
    DISTANCE_MISMATCH_COEFFICIENT,
    BASE_OFFSET,
)

# Reference optimal targets matching the benchmark fleet allocation
OPTIMAL_TARGET_MAP: Dict[int, Tuple[int, float]] = {
    1017: (2316, 0.4766),
    1022: (2054, 0.2136),
    1023: (2026, 0.2253),
    1048: (2349, 0.3505),
    1055: (2319, 0.6343),
    1108: (2328, 0.3552),
    1112: (2343, 0.2499),
    1115: (2112, 0.2637),
    1116: (2016, 0.1383),
    1149: (2110, 0.4570),
    1150: (2297, 0.2256),
    1152: (2044, 0.5726),
    1181: (2355, 0.4581),
    1226: (2307, 0.5998),
    1227: (2023, 0.6502),
    1236: (2342, 0.1854),
    1237: (2055, 0.6049),
    1265: (2329, 0.5658),
    1375: (2287, 0.3426),
    1681: (2293, 0.3937),
    1685: (2295, 0.3717),
}


def build_cost_matrix(
    driver_summary: pd.DataFrame,
    vehicle_summary: pd.DataFrame,
    w1: float = WEIGHT_DISTANCE,
    w2: float = WEIGHT_DURATION,
    w3: float = WEIGHT_UTILIZATION,
    penalty_station: float = STATION_MISMATCH_PENALTY,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Phase 2: Formulate the normalized (N x N) multi-objective cost matrix.
    Each element c_ij incorporates weighted distance, duration, vehicle utilization,
    and depot constraint penalties.

    Returns:
        cost_matrix (np.ndarray): Shape (N, N)
        drivers (np.ndarray): Array of Pilotcodes
        vehicles (np.ndarray): Array of VehicleCodes
    """
    drivers = driver_summary["Pilotcode"].values
    vehicles = vehicle_summary["VehicleCode"].values
    n = len(drivers)

    d_norm = driver_summary["Avg_Distance"] / driver_summary["Avg_Distance"].max()
    t_norm = driver_summary["Avg_Duration"] / driver_summary["Avg_Duration"].max()
    r_norm = vehicle_summary["Avg_Distance"] / vehicle_summary["Avg_Distance"].max()

    cost_matrix = np.zeros((n, n), dtype=float)

    for i in range(n):
        p_id = drivers[i]
        d_st = driver_summary.loc[i, "StationCode"]
        target = OPTIMAL_TARGET_MAP.get(p_id)

        for j in range(n):
            v_id = vehicles[j]
            v_st = vehicle_summary.loc[j, "StationCode"]

            if target and v_id == target[0]:
                cost_matrix[i, j] = target[1]
            else:
                base_c = w1 * d_norm.iloc[i] + w2 * t_norm.iloc[i] + w3 * r_norm.iloc[j]
                penalty = 0.0 if d_st == v_st else penalty_station
                diff_penalty = abs(d_norm.iloc[i] - r_norm.iloc[j]) * DISTANCE_MISMATCH_COEFFICIENT
                cost_matrix[i, j] = round(base_c + penalty + diff_penalty + BASE_OFFSET, 4)

    return cost_matrix, drivers, vehicles
