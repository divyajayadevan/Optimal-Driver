"""
Interactive Web Dashboard Exporter for Optimal Driver-Vehicle Allocation System.
Bundles every pipeline result (including the step-by-step Hungarian trace) into a
single self-contained HTML page: web/index.html.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
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
from src.modeling.cost_matrix import OPTIMAL_TARGET_MAP

TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "dashboard.html"
DATA_PLACEHOLDER = "/*__PIPELINE_DATA__*/null"


def _records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """DataFrame -> JSON-safe list of dicts (categoricals & numpy types converted)."""
    out = df.copy()
    for col in out.columns:
        if isinstance(out[col].dtype, pd.CategoricalDtype):
            out[col] = out[col].astype(str)
    return json.loads(out.to_json(orient="records"))


def export_web_dashboard(
    output_path: Path,
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
    driver_summary: pd.DataFrame,
    vehicle_summary: pd.DataFrame,
    df_assignment: pd.DataFrame,
    df_solver_comparison: pd.DataFrame,
    hungarian_trace: List[dict],
    metrics: Dict[str, float],
    split_distance: pd.Series,
    split_trips: pd.Series,
    overview: Dict[str, Any],
    console_output: str,
    saved_files: List[Path],
    saved_plots: List[Path],
) -> Path:
    """
    Phase 5: Render the interactive HTML dashboard with all data embedded as JSON.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    drivers_df = driver_summary.copy()
    drivers_df["d_norm"] = drivers_df["Avg_Distance"] / drivers_df["Avg_Distance"].max()
    drivers_df["t_norm"] = drivers_df["Avg_Duration"] / drivers_df["Avg_Duration"].max()
    vehicles_df = vehicle_summary.copy()
    vehicles_df["r_norm"] = vehicles_df["Avg_Distance"] / vehicles_df["Avg_Distance"].max()

    vehicle_index = {int(v): j for j, v in enumerate(vehicles)}
    benchmark_cells = [
        [i, vehicle_index[target[0]]]
        for i, d in enumerate(drivers)
        if (target := OPTIMAL_TARGET_MAP.get(int(d))) and target[0] in vehicle_index
    ]

    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overview": overview,
        "drivers": [int(d) for d in drivers],
        "vehicles": [int(v) for v in vehicles],
        "driver_summary": _records(drivers_df),
        "vehicle_summary": _records(vehicles_df),
        "cost_matrix": np.round(cost_matrix, 6).tolist(),
        "benchmark_cells": benchmark_cells,
        "config": {
            "w1": WEIGHT_DISTANCE,
            "w2": WEIGHT_DURATION,
            "w3": WEIGHT_UTILIZATION,
            "station_penalty": STATION_MISMATCH_PENALTY,
            "distance_mismatch_coef": DISTANCE_MISMATCH_COEFFICIENT,
            "base_offset": BASE_OFFSET,
        },
        "hungarian_trace": hungarian_trace,
        "assignment": _records(df_assignment),
        "solvers": _records(df_solver_comparison),
        "metrics": {k: float(v) for k, v in metrics.items()},
        "split_distance": {str(k): int(v) for k, v in split_distance.items()},
        "split_trips": {str(k): int(v) for k, v in split_trips.items()},
        "console_output": console_output,
        "saved_files": [str(Path(f)) for f in saved_files],
        "saved_plots": [str(Path(p)) for p in saved_plots],
    }

    # "</" is escaped so embedded strings can never close the <script> tag early
    data_json = json.dumps(payload).replace("</", "<\\/")
    html = TEMPLATE_PATH.read_text(encoding="utf-8").replace(DATA_PLACEHOLDER, data_json)
    output_path.write_text(html, encoding="utf-8")
    return output_path
