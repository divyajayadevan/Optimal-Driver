from typing import Dict, List
from pathlib import Path
import pandas as pd


def display_dashboard(
    shifts_count: int,
    trips_count: int,
    avg_shift_dur: float,
    avg_shift_dist: float,
    min_trips: int,
    max_trips: int,
    n_drivers: int,
    n_vehicles: int,
    df_assignment: pd.DataFrame,
    metrics: Dict[str, float],
    split_distance: pd.Series,
    split_trips: pd.Series,
    saved_files: List[Path],
) -> None:
    """
    Phase 5: Display comprehensive decision-support dashboard in the terminal.
    """
    print("=" * 80)
    print("      OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM (DECISION SUPPORT)")
    print("=" * 80)

    print("\n[PHASE 1] DATA INGESTION & PREPROCESSING")
    print(f"  • Shift Records Ingested  : {shifts_count}")
    print(f"  • Trip Transactions       : {trips_count}")
    print(f"  • Avg Shift Duration (Ti) : {avg_shift_dur:.2f} hours")
    print(f"  • Avg Shift Distance (Di) : {avg_shift_dist:.2f} km")
    print(f"  • Trips per Vehicle Range : {min_trips} to {max_trips} trips")

    print("\n[PHASE 2 & 3] COST MATRIX FORMULATION & HUNGARIAN OPTIMIZATION")
    print(f"  • Driver Pool (N={n_drivers})  ↔  Vehicle Fleet (N={n_vehicles})")
    print("  • Optimal Pairing Schedule:")
    print("-" * 60)
    print(
        df_assignment.to_string(
            index=False,
            formatters={"CellCost": "{:>8.4f}".format, "SameStation": "{!s:>11}".format},
        )
    )
    print("-" * 60)

    print("\n[PHASE 4] WORKLOAD FAIRNESS & FLEET UTILIZATION BENCHMARKS")
    print(f"  • Existing Baseline Total Cost : {metrics['baseline_cost']:.4f}")
    print(f"  • Optimized Total Cost (Z)     : {metrics['optimized_cost']:.4f}")
    print(f"  • Cost Reduction (CR%)         : {metrics['cost_reduction_pct']:.2f}%")
    print(f"  • Mean Workload (W̄)           : {metrics['mean_workload']:.2f} km")
    print(f"  • Workload Variance (σ²)       : {metrics['variance_workload']:.2f}")
    print(f"  • Workload Std Deviation (σ)   : {metrics['std_workload']:.2f} km")
    print(f"  • Baseline WBI                 : {metrics['baseline_wbi']:.4f}")
    print(f"  • Optimized WBI                : {metrics['wbi']:.4f} (+{metrics['wbi_improvement_pct']:.2f}%)")

    print("\n  • Fleet Utilization Breakdown (Distance Method):")
    for cat, count in split_distance.items():
        print(f"      - {cat:<10}: {count:>2} vehicles")

    print("\n  • Fleet Utilization Breakdown (Trip Count Method):")
    for cat, count in split_trips.items():
        print(f"      - {cat:<10}: {count:>2} vehicles")

    print("\n[PHASE 5] GENERATED ARTIFACTS")
    for file_path in saved_files:
        print(f"  ✓ {file_path}")

    print("\n" + "=" * 80)
    print("               PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")
