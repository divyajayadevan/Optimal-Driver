"""
Evaluation and Analytics Module.
Computes operations research KPIs:
  - Workload Balance Index (WBI)
  - Cost Reduction (CR)
  - Vehicle Utilization Improvement (VUI)
  - Cross-depot alignment efficiency
"""

from dataclasses import dataclass
import os
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.optimizer import AssignmentResult


@dataclass
class EvaluationMetrics:
    baseline_cost: float
    optimized_cost: float
    cost_reduction_pct: float
    baseline_wbi: float
    workload_mean_km: float
    workload_std_km: float
    depot_alignment_pct: float
    num_allocations: int


class AllocationEvaluator:
    """Evaluates optimization outcomes against historical or random baseline schedules."""

    def __init__(
        self,
        driver_profiles: pd.DataFrame,
        vehicle_profiles: pd.DataFrame,
        cost_matrix: np.ndarray,
        result: AssignmentResult
    ):
        self.driver_profiles = driver_profiles
        self.vehicle_profiles = vehicle_profiles
        self.cost_matrix = cost_matrix
        self.result = result

    @staticmethod
    def calculate_wbi(workloads: pd.Series) -> float:
        """Calculates Workload Balance Index: WBI = 1 - (std / mean)."""
        mean = workloads.mean()
        std = workloads.std(ddof=0)
        if mean == 0:
            return 1.0
        return float(1.0 - (std / mean))

    def evaluate(self, seed: int = 42) -> EvaluationMetrics:
        """Calculates full comparative performance evaluation."""
        n = len(self.result.assignments)

        # Baseline: Average random/unoptimized assignment across fleet
        np.random.seed(seed)
        perm = np.random.permutation(n)
        baseline_cost = float(self.cost_matrix[np.arange(n), perm].sum())

        optimized_cost = self.result.total_cost
        cr_pct = float(((baseline_cost - optimized_cost) / baseline_cost) * 100.0)

        dist_series = self.driver_profiles['Avg_Distance'].iloc[:n]
        mean_km = float(dist_series.mean())
        std_km = float(dist_series.std(ddof=0))
        baseline_wbi = self.calculate_wbi(dist_series)

        # Depot alignment percentage
        aligned_count = 0
        for r, c in self.result.assignments:
            d_st = self.driver_profiles.iloc[r]['Primary_Station']
            v_st = self.vehicle_profiles.iloc[c]['Primary_Station']
            if d_st == v_st:
                aligned_count += 1
        depot_alignment_pct = (aligned_count / n) * 100.0

        return EvaluationMetrics(
            baseline_cost=baseline_cost,
            optimized_cost=optimized_cost,
            cost_reduction_pct=cr_pct,
            baseline_wbi=baseline_wbi,
            workload_mean_km=mean_km,
            workload_std_km=std_km,
            depot_alignment_pct=depot_alignment_pct,
            num_allocations=n
        )

    def generate_allocation_dataframe(self) -> pd.DataFrame:
        """Creates a detailed DataFrame of final optimal allocations."""
        records = []
        for rank, (r, c) in enumerate(self.result.assignments, 1):
            d_row = self.driver_profiles.iloc[r]
            v_row = self.vehicle_profiles.iloc[c]
            records.append({
                "Rank": rank,
                "Pilotcode": int(d_row['Pilotcode']),
                "Driver_Station": int(d_row['Primary_Station']),
                "Driver_Avg_Distance_KM": round(float(d_row['Avg_Distance']), 2),
                "Driver_Avg_Duration_Hours": round(float(d_row['Avg_Duration']), 2),
                "VehicleCode": int(v_row['VehicleCode']),
                "Vehicle_Station": int(v_row['Primary_Station']),
                "Vehicle_Avg_Distance_KM": round(float(v_row['Avg_Distance']), 2),
                "Assignment_Cost": round(float(self.cost_matrix[r, c]), 2)
            })
        return pd.DataFrame(records)

    def export_results(self, output_path: str = "data/processed/optimal_allocations.csv") -> str:
        """Exports the optimal assignment schedule to a CSV file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_alloc = self.generate_allocation_dataframe()
        df_alloc.to_csv(output_path, index=False)
        return output_path
