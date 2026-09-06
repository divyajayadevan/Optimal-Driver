from typing import Dict
import pandas as pd
from src.config import BASELINE_TOTAL_COST, BASELINE_WBI


def compute_workload_metrics(driver_summary: pd.DataFrame, optimized_cost: float) -> Dict[str, float]:
    """
    Phase 4: Workload Balance Evaluation.
    Computes mean workload, variance (σ²), standard deviation (σ),
    Workload Balance Index (WBI = 1 - σ / W̄), and Cost Reduction (CR%).
    """
    mean_workload = float(driver_summary["Avg_Distance"].mean())
    var_workload = float(driver_summary["Avg_Distance"].var(ddof=0))
    std_workload = float(driver_summary["Avg_Distance"].std(ddof=0))

    wbi = 1.0 - (std_workload / mean_workload) if mean_workload > 0 else 0.0

    cost_reduction = (
        ((BASELINE_TOTAL_COST - optimized_cost) / BASELINE_TOTAL_COST) * 100.0
        if BASELINE_TOTAL_COST > 0
        else 0.0
    )

    wbi_improvement = ((wbi - BASELINE_WBI) / BASELINE_WBI) * 100.0 if BASELINE_WBI > 0 else 0.0

    return {
        "mean_workload": mean_workload,
        "variance_workload": var_workload,
        "std_workload": std_workload,
        "wbi": wbi,
        "baseline_wbi": BASELINE_WBI,
        "wbi_improvement_pct": wbi_improvement,
        "baseline_cost": BASELINE_TOTAL_COST,
        "optimized_cost": optimized_cost,
        "cost_reduction_pct": cost_reduction,
    }
