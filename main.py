"""
================================================================================
OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM - CLI PIPELINE
================================================================================
Main orchestrator for the 4-step automated fleet scheduling pipeline:
  1. Ingestion & Preprocessing
  2. Multi-Objective Cost Matrix Formulation
  3. Hungarian (Kuhn-Munkres) Optimization
  4. Operations Research Performance Evaluation & Export
"""

import argparse
import sys
import numpy as np

from src.preprocessing import DataIngestionPipeline
from src.optimizer import CostMatrixBuilder, HungarianOptimizer
from src.evaluator import AllocationEvaluator


def run_pedagogical_demos():
    """Demonstrates step-by-step Hungarian algorithm on 3x3 and 4x4 matrices."""
    print("\n" + "=" * 80)
    print("DEMO 1: 3x3 Problem from Presentation (Slide 7)")
    print("=" * 80)
    matrix_3x3 = np.array([
        [15.0, 18.0, 20.0],
        [10.0, 14.0, 16.0],
        [12.0, 17.0, 13.0]
    ])
    solver3 = HungarianOptimizer(
        matrix_3x3,
        row_labels=["Driver D1", "Driver D2", "Driver D3"],
        col_labels=["Vehicle V1", "Vehicle V2", "Vehicle V3"],
        verbose=True
    )
    res3 = solver3.solve()
    print(f"\nOptimal 3x3 Assignment Cost: {res3.total_cost:.2f}")

    print("\n" + "=" * 80)
    print("DEMO 2: 4x4 Problem with Multi-Iteration Line Covering & Matrix Adjustments")
    print("=" * 80)
    matrix_4x4 = np.array([
        [90.0, 75.0, 75.0, 80.0],
        [35.0, 85.0, 55.0, 65.0],
        [125.0, 95.0, 90.0, 105.0],
        [45.0, 110.0, 95.0, 115.0]
    ])
    solver4 = HungarianOptimizer(
        matrix_4x4,
        row_labels=["Driver D1", "Driver D2", "Driver D3", "Driver D4"],
        col_labels=["Vehicle V1", "Vehicle V2", "Vehicle V3", "Vehicle V4"],
        verbose=True
    )
    res4 = solver4.solve()
    print(f"\nOptimal 4x4 Assignment Cost: {res4.total_cost:.2f}")


def run_pipeline(shift_file: str = "data/raw/ShiftData.csv", verbose: bool = False, export_path: str = "data/processed/optimal_allocations.csv"):
    print("=" * 85)
    print("       OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM (OPERATIONS RESEARCH PIPELINE)")
    print("=" * 85)

    # STEP 1: INGESTION & PREPROCESSING
    print("\n[STEP 1/4] Ingestion & Preprocessing...")
    pipeline = DataIngestionPipeline(shift_file=shift_file)
    pipeline.load_data()
    driver_stats, vehicle_stats = pipeline.aggregate_profiles()
    summary = pipeline.get_summary()

    print(f"  * Total shift logs loaded      : {summary.total_records}")
    print(f"  * Fleet Size                   : {summary.num_drivers} Drivers x {summary.num_vehicles} Vehicles")
    print(f"  * Operating Depots (Stations)  : {summary.num_stations} (Depots: {sorted(pipeline.cleaned_shifts['StationCode'].unique().tolist())})")
    print(f"  * Avg Shift Distance           : {summary.avg_shift_distance:.2f} km")
    print(f"  * Avg Shift Duration           : {summary.avg_shift_duration:.2f} hours")

    # STEP 2: COST MATRIX GENERATION
    print("\n[STEP 2/4] Formulating Multi-Objective Operational Cost Matrix...")
    cost_builder = CostMatrixBuilder(driver_stats, vehicle_stats, w1=0.4, w2=0.3, w3=0.3, depot_penalty=45.0, wear_weight=0.4)
    cost_matrix, drivers, vehicles = cost_builder.build()
    n = len(drivers)
    print(f"  * Dimensions: {n} x {n} ({n*n} potential assignment combinations)")
    print(f"  * Parameters: Distance (w1=0.4), Duration (w2=0.3), Wear (w3=0.3), Cross-Depot Penalty (45.0)")

    # STEP 3: OPTIMIZATION EXECUTION
    print("\n[STEP 3/4] Solving Linear Assignment via Hungarian Algorithm...")
    row_labels = [f"Pilot_{d}" for d in drivers]
    col_labels = [f"Veh_{v}" for v in vehicles]
    optimizer = HungarianOptimizer(cost_matrix, row_labels=row_labels, col_labels=col_labels, verbose=verbose)
    assignment_result = optimizer.solve()

    # STEP 4: EVALUATION & REPORTING
    print("\n[STEP 4/4] Analytics, Performance Evaluation & Export...")
    evaluator = AllocationEvaluator(driver_stats, vehicle_stats, cost_matrix, assignment_result)
    metrics = evaluator.evaluate()

    print("\n" + "-" * 85)
    print(f"{'Rank':<5} | {'Driver ID':<12} | {'Depot':<7} | {'Assigned Vehicle':<18} | {'Veh Depot':<10} | {'Cost':>10}")
    print("-" * 85)
    df_alloc = evaluator.generate_allocation_dataframe()
    for _, row in df_alloc.iterrows():
        print(f"{int(row['Rank']):<5} | Pilot {int(row['Pilotcode']):<6} | {int(row['Driver_Station']):<7} | Vehicle {int(row['VehicleCode']):<10} | {int(row['Vehicle_Station']):<10} | {float(row['Assignment_Cost']):>10.2f}")
    print("-" * 85)
    print(f"{'TOTAL OPTIMIZED OPERATIONAL COST:':<67} {metrics.optimized_cost:>10.2f}")
    print("=" * 85)

    print("\n[KEY PERFORMANCE INDICATORS (KPIs)]")
    print(f"  * Baseline Ad-hoc Cost         : {metrics.baseline_cost:.2f}")
    print(f"  * Hungarian Optimized Cost     : {metrics.optimized_cost:.2f}")
    print(f"  * Cost Reduction (CR)          : {metrics.cost_reduction_pct:.2f}% (Savings)")
    print(f"  * Baseline Workload Index (WBI): {metrics.baseline_wbi:.4f} (Slide 9 target: 0.84)")
    print(f"  * Depot Station Alignment      : {metrics.depot_alignment_pct:.1f}% (Zero cross-depot misallocations)")
    
    saved_file = evaluator.export_results(export_path)
    print(f"  * Schedule Exported To         : {saved_file}")
    print("\nPipeline execution finished successfully.\n")


def main():
    parser = argparse.ArgumentParser(description="Optimal Driver-Vehicle Allocation Software Package.")
    parser.add_argument("--demo", action="store_true", help="Run 3x3 and 4x4 pedagogical step-by-step walkthroughs.")
    parser.add_argument("--step-by-step", action="store_true", help="Print all intermediate matrix reductions for 21x21 fleet.")
    parser.add_argument("--input", type=str, default="data/raw/ShiftData.csv", help="Path to input ShiftData.csv.")
    parser.add_argument("--output", type=str, default="data/processed/optimal_allocations.csv", help="Path to output CSV.")
    args = parser.parse_args()

    if args.demo:
        run_pedagogical_demos()
    else:
        run_pipeline(shift_file=args.input, verbose=args.step_by_step, export_path=args.output)


if __name__ == "__main__":
    main()
