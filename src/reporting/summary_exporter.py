from typing import List, Optional
from pathlib import Path
import numpy as np
import pandas as pd

from src.config import (
    PROCESSED_DATA_DIR,
    OUTPUT_ASSIGNMENT_FILE,
    OUTPUT_COST_MATRIX_FILE,
    OUTPUT_VEHICLE_UTIL_FILE,
    OUTPUT_DRIVER_SUMMARY_FILE,
)


def export_pipeline_artifacts(
    df_assignment: pd.DataFrame,
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
    vehicle_summary: pd.DataFrame,
    driver_summary: pd.DataFrame,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """
    Phase 5: Export all decision-support CSV report artifacts.
    """
    out_dir = output_dir or PROCESSED_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    assignment_path = out_dir / "optimal_assignment.csv"
    cost_mat_path = out_dir / "cost_matrix_21x21.csv"
    veh_util_path = out_dir / "vehicle_utilization.csv"
    driver_sum_path = out_dir / "driver_summary.csv"

    # Save artifacts
    df_assignment.to_csv(assignment_path, index=False)

    df_cost_mat = pd.DataFrame(cost_matrix, index=drivers, columns=vehicles)
    df_cost_mat.to_csv(cost_mat_path)

    vehicle_summary.to_csv(veh_util_path, index=False)
    driver_summary.to_csv(driver_sum_path, index=False)

    return [assignment_path, cost_mat_path, veh_util_path, driver_sum_path]
