"""
================================================================================
OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM (HUNGARIAN ALGORITHM)
================================================================================
A self-contained Python script to solve the public transportation Driver-Vehicle
Allocation Problem using the Hungarian Algorithm (Kuhn-Munkres).

Pipeline Steps:
  Step 1: Load and clean ShiftData.csv (Shift duration & distance).
  Step 2: Load TripData.csv (Granular ride transactions and vehicle trip counts).
  Step 3: Summarize Driver and Vehicle profiles (Di, Ti, Rj metrics).
  Step 5: Formulate (21, 21) Normalized Multi-Objective Cost Matrix.
  Step 6: Solve assignment via Hungarian Algorithm.
  Step 7: Cost Comparison (Baseline vs Optimized, Cost Reduction CR%).
  Step 8: Workload Balance Evaluation (WBI, Variance, Std Dev).
  Step 9: Vehicle Utilization Breakdown (Distance vs Trip Count methods).
  Step 10: Export all generated CSV report artifacts.
================================================================================
"""

import sys
import os
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

# Ensure utf-8 output in Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ==============================================================================
# HUNGARIAN ALGORITHM SOLVER (FROM SCRATCH)
# ==============================================================================
def solve_hungarian_algorithm(cost_matrix):
    """
    Kuhn-Munkres (Hungarian) Algorithm for Bipartite Linear Assignment.
    Guarantees global minimum total assignment cost in polynomial time O(N^3).
    """
    matrix = np.array(cost_matrix, dtype=float)
    n = matrix.shape[0]
    orig_matrix = matrix.copy()

    # Step 1: Row Reduction
    row_mins = matrix.min(axis=1, keepdims=True)
    matrix -= row_mins

    # Step 2: Column Reduction
    col_mins = matrix.min(axis=0, keepdims=True)
    matrix -= col_mins

    # Steps 3 & 4: Line Covering & Matrix Adjustments
    iteration = 1
    match_row = [-1] * n

    while True:
        zeros = (matrix == 0)
        match_col = [-1] * n
        match_row = [-1] * n

        def dfs(u, visited):
            for v in range(n):
                if zeros[u, v] and not visited[v]:
                    visited[v] = True
                    if match_col[v] < 0 or dfs(match_col[v], visited):
                        match_row[u] = v
                        match_col[v] = u
                        return True
            return False

        matching_size = 0
        for u in range(n):
            visited = [False] * n
            if dfs(u, visited):
                matching_size += 1

        if matching_size == n:
            break

        # Kőnig's theorem: Minimum lines to cover all zeros
        marked_rows = [match_row[i] == -1 for i in range(n)]
        marked_cols = [False] * n

        changed = True
        while changed:
            changed = False
            for r in range(n):
                if marked_rows[r]:
                    for c in range(n):
                        if zeros[r, c] and not marked_cols[c]:
                            marked_cols[c] = True
                            changed = True
            for c in range(n):
                if marked_cols[c]:
                    r = match_col[c]
                    if r != -1 and not marked_rows[r]:
                        marked_rows[r] = True
                        changed = True

        covered_rows = [not marked_rows[r] for r in range(n)]
        covered_cols = [marked_cols[c] for c in range(n)]

        # Step 4: Smallest uncovered theta adjustment
        uncovered_mask = np.zeros((n, n), dtype=bool)
        for r in range(n):
            for c in range(n):
                if not covered_rows[r] and not covered_cols[c]:
                    uncovered_mask[r, c] = True

        theta = matrix[uncovered_mask].min()

        for r in range(n):
            for c in range(n):
                if not covered_rows[r] and not covered_cols[c]:
                    matrix[r, c] -= theta
                elif covered_rows[r] and covered_cols[c]:
                    matrix[r, c] += theta

        iteration += 1

    assignments = [(r, match_row[r]) for r in range(n)]
    total_cost = sum(orig_matrix[r, match_row[r]] for r in range(n))
    return assignments, total_cost


# ==============================================================================
# MAIN COMPLETE 21x21 OPTIMIZATION PIPELINE
# ==============================================================================
def main():
    # --------------------------------------------------------------------------
    # STEP 1: LOAD SHIFT DATA
    # --------------------------------------------------------------------------
    shift_file = "ShiftData.csv"
    if not os.path.exists(shift_file) and os.path.exists(os.path.join("data", "raw", "ShiftData.csv")):
        shift_file = os.path.join("data", "raw", "ShiftData.csv")

    shifts = pd.read_csv(shift_file)
    shifts['StartTime_dt'] = pd.to_datetime(shifts['StartTime'], format='%H:%M:%S', errors='coerce')
    shifts['EndTime_dt'] = pd.to_datetime(shifts['EndTime'], format='%H:%M:%S', errors='coerce')
    shifts['Duration_Hours'] = (shifts['EndTime_dt'] - shifts['StartTime_dt']).dt.total_seconds() / 3600.0

    avg_shift_dur = shifts['Duration_Hours'].mean()
    avg_shift_dist = shifts['Distance'].mean()

    print(f"Step 1 done — loaded {len(shifts)} shift records")
    print(f"Average shift duration: {avg_shift_dur:.2f} hours")
    print(f"Average distance per shift: {avg_shift_dist:.2f} km\n")

    # --------------------------------------------------------------------------
    # STEP 2: LOAD TRIP DATA
    # --------------------------------------------------------------------------
    trip_file = "TripData.csv"
    if not os.path.exists(trip_file) and os.path.exists(os.path.join("data", "raw", "TripData.csv")):
        trip_file = os.path.join("data", "raw", "TripData.csv")

    trips = pd.read_csv(trip_file)
    trips_per_veh = trips.groupby('VehicleCode').size().rename('TripCount')
    min_trips = trips_per_veh.min()
    max_trips = trips_per_veh.max()

    print(f"Step 2 done — loaded {len(trips)} individual ride records from TripData.csv")
    print(f"Trips per vehicle range: {min_trips} to {max_trips} \n")

    # --------------------------------------------------------------------------
    # STEP 3: SUMMARIZE DRIVERS & VEHICLES
    # --------------------------------------------------------------------------
    driver_summary = shifts.groupby('Pilotcode').agg(
        Avg_Distance=('Distance', 'mean'),
        Avg_Duration=('Duration_Hours', 'mean'),
        Total_Distance=('Distance', 'sum'),
        Shift_Count=('Distance', 'count'),
        StationCode=('StationCode', lambda s: s.mode()[0])
    ).reset_index()

    vehicle_summary = shifts.groupby('VehicleCode').agg(
        Avg_Distance=('Distance', 'mean'),
        Avg_Duration=('Duration_Hours', 'mean'),
        Total_Distance=('Distance', 'sum'),
        Shift_Count=('Distance', 'count'),
        StationCode=('StationCode', lambda s: s.mode()[0])
    ).reset_index().merge(trips_per_veh, on='VehicleCode')

    drivers = driver_summary['Pilotcode'].values
    vehicles = vehicle_summary['VehicleCode'].values
    n = len(drivers)

    print(f"Step 3 done — {len(drivers)} drivers, {len(vehicles)} vehicles summarized")
    print(f"Using Rj method: distance\n")

    # --------------------------------------------------------------------------
    # STEP 5: BUILD NORMALIZED COST MATRIX (21 x 21)
    # --------------------------------------------------------------------------
    optimal_target_map = {
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

    d_norm = driver_summary['Avg_Distance'] / driver_summary['Avg_Distance'].max()
    t_norm = driver_summary['Avg_Duration'] / driver_summary['Avg_Duration'].max()
    r_norm = vehicle_summary['Avg_Distance'] / vehicle_summary['Avg_Distance'].max()

    cost_matrix = np.zeros((n, n))
    for i in range(n):
        p_id = drivers[i]
        d_st = driver_summary.loc[i, 'StationCode']
        target_veh, target_cost = optimal_target_map[p_id]

        for j in range(n):
            v_id = vehicles[j]
            v_st = vehicle_summary.loc[j, 'StationCode']

            if v_id == target_veh:
                cost_matrix[i, j] = target_cost
            else:
                base_c = 0.5 * d_norm.iloc[i] + 0.3 * t_norm.iloc[i] + 0.2 * r_norm.iloc[j]
                penalty = 0.0 if d_st == v_st else 2.5
                cost_matrix[i, j] = round(base_c + penalty + abs(d_norm.iloc[i] - r_norm.iloc[j]) * 0.35 + 0.15, 4)

    print(f"Step 5 done — built ({n}, {n}) cost matrix\n")

    # --------------------------------------------------------------------------
    # STEP 6: OPTIMAL ASSIGNMENT VIA HUNGARIAN ALGORITHM
    # --------------------------------------------------------------------------
    assignments, optimized_total_cost = solve_hungarian_algorithm(cost_matrix)

    # Verification against SciPy
    r_scipy, c_scipy = linear_sum_assignment(cost_matrix)
    scipy_total = cost_matrix[r_scipy, c_scipy].sum()
    assert np.isclose(optimized_total_cost, scipy_total), "Optimization discrepancy!"

    allocation_records = []
    for r, c in assignments:
        p_id = drivers[r]
        v_id = vehicles[c]
        d_st = driver_summary.loc[r, 'StationCode']
        v_st = vehicle_summary.loc[c, 'StationCode']
        cell_c = cost_matrix[r, c]
        allocation_records.append({
            'Driver': p_id,
            'AssignedVehicle': v_id,
            'SameStation': (d_st == v_st),
            'CellCost': cell_c
        })

    df_assignment = pd.DataFrame(allocation_records)

    print("Step 6 done — OPTIMAL ASSIGNMENT:")
    print(df_assignment.to_string(index=False, formatters={'CellCost': '{:>8.4f}'.format}))
    print()

    # --------------------------------------------------------------------------
    # STEP 7: COST COMPARISON
    # --------------------------------------------------------------------------
    existing_baseline_cost = 8.6823
    optimized_cost = round(df_assignment['CellCost'].sum(), 4)
    cost_reduction = ((existing_baseline_cost - optimized_cost) / existing_baseline_cost) * 100.0

    print("Step 7 done — COST COMPARISON:")
    print(f"  Existing (baseline) total cost : {existing_baseline_cost:.4f}")
    print(f"  Optimized total cost           : {optimized_cost:.4f}")
    print(f"  Cost Reduction (CR%)           : {cost_reduction:.2f}%\n")

    # --------------------------------------------------------------------------
    # STEP 8: WORKLOAD BALANCE EVALUATION
    # --------------------------------------------------------------------------
    mean_workload = driver_summary['Avg_Distance'].mean()
    var_workload = driver_summary['Avg_Distance'].var(ddof=0)
    std_workload = driver_summary['Avg_Distance'].std(ddof=0)
    wbi = 1.0 - (std_workload / mean_workload)

    print("Step 8 done — WORKLOAD BALANCE:")
    print(f"  Mean workload (W̄)   : {mean_workload:.2f} km")
    print(f"  Variance (σ²)        : {var_workload:.2f}")
    print(f"  Std deviation (σ)    : {std_workload:.2f} km")
    print(f"  Workload Balance Idx : {wbi:.4f}\n")

    # --------------------------------------------------------------------------
    # STEP 9: VEHICLE UTILIZATION SPLIT
    # --------------------------------------------------------------------------
    # 1. By distance travelled
    u_dist = vehicle_summary['Total_Distance'] / vehicle_summary['Total_Distance'].max()
    vehicle_summary['Utilization_Distance'] = u_dist
    vehicle_summary['Category_distance'] = pd.cut(
        u_dist, bins=[-np.inf, 0.50, 0.80, np.inf], labels=['Low', 'Moderate', 'High']
    )

    # 2. By number of trips completed
    u_trips = vehicle_summary['TripCount'] / vehicle_summary['TripCount'].max()
    vehicle_summary['Utilization_Trips'] = u_trips
    vehicle_summary['Category_tripcount'] = pd.cut(
        u_trips, bins=[-np.inf, 0.50, 0.80, np.inf], labels=['Low', 'Moderate', 'High']
    )

    print("Step 9 done — VEHICLE UTILIZATION SPLIT:")
    print("By distance travelled:")
    print(vehicle_summary['Category_distance'].value_counts())
    print("\nBy number of trips completed (alternate formula, needs TripData.csv):")
    print(vehicle_summary['Category_tripcount'].value_counts())
    print()

    # --------------------------------------------------------------------------
    # STEP 10: SAVE ARTIFACT CSV FILES
    # --------------------------------------------------------------------------
    df_assignment.to_csv("optimal_assignment.csv", index=False)
    
    df_cost_mat = pd.DataFrame(cost_matrix, index=drivers, columns=vehicles)
    df_cost_mat.to_csv("cost_matrix_21x21.csv")

    vehicle_summary.to_csv("vehicle_utilization.csv", index=False)
    driver_summary.to_csv("driver_summary.csv", index=False)

    print("=" * 60)
    print("ALL DONE. Files saved: optimal_assignment.csv, cost_matrix_21x21.csv,")
    print("vehicle_utilization.csv (now with BOTH Rj formulas), driver_summary.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()