"""
================================================================================
OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM
================================================================================
All-in-One Optimization, Benchmarking, Excel Reporting & Visual Analytics Pipeline.

Run:
    python main.py
"""

import io
import sys
import time
import argparse
import webbrowser
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import savemat
from scipy.optimize import linear_sum_assignment

# Ensure UTF-8 output encoding in Windows shells
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.ingestion.loader import load_shift_data, load_trip_data
from src.ingestion.preprocessor import summarize_drivers, summarize_vehicles
from src.modeling.cost_matrix import build_cost_matrix
from src.modeling.hungarian_solver import solve_assignment, solve_hungarian_algorithm
from src.modeling.alternative_solvers import solve_with_pulp, solve_with_ortools
from src.analytics.workload import compute_workload_metrics
from src.analytics.utilization import compute_vehicle_utilization
from src.reporting.summary_exporter import export_pipeline_artifacts
from src.reporting.excel_exporter import export_excel_workbook
from src.reporting.plotter import generate_all_plots
from src.reporting.console_view import display_dashboard
from src.reporting.web_exporter import export_web_dashboard


def run_pipeline(
    shift_path: Path = None,
    trip_path: Path = None,
    output_dir: Path = None,
    verbose: bool = True,
    open_web: bool = False,
):
    """
    Execute full optimization workflow with all solvers, Excel exports, and visual plots.
    """
    output_dir = Path(output_dir) if output_dir else Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = Path("plots")
    plots_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------------------
    # PHASE 1: DATA INGESTION & PREPROCESSING
    # --------------------------------------------------------------------------
    shifts = load_shift_data(shift_path)
    trips = load_trip_data(trip_path)

    avg_shift_dur = float(shifts["Duration_Hours"].mean())
    avg_shift_dist = float(shifts["Distance"].mean())
    trips_per_veh = trips.groupby("VehicleCode").size()

    driver_summary = summarize_drivers(shifts)
    vehicle_summary = summarize_vehicles(shifts, trips)

    n_drivers = len(driver_summary)
    n_vehicles = len(vehicle_summary)

    # --------------------------------------------------------------------------
    # PHASE 2: COST MATRIX FORMULATION
    # --------------------------------------------------------------------------
    cost_matrix, drivers, vehicles = build_cost_matrix(driver_summary, vehicle_summary)

    # --------------------------------------------------------------------------
    # PHASE 3: MULTI-SOLVER BENCHMARKING (Hungarian, SciPy, PuLP, OR-Tools)
    # --------------------------------------------------------------------------
    solver_records = []

    # 1. Custom Hungarian (timed without tracing; traced separately for the web view)
    t0 = time.perf_counter()
    h_pairs, h_cost = solve_hungarian_algorithm(cost_matrix)
    t_h = (time.perf_counter() - t0) * 1000
    hungarian_trace = []
    solve_hungarian_algorithm(cost_matrix, trace=hungarian_trace)
    solver_records.append({
        "Tool / Solver": "Python (Custom Kuhn-Munkres)",
        "Category": "Bipartite Graph Matching",
        "Optimal Cost (Z)": round(h_cost, 4),
        "Execution Time (ms)": round(t_h, 3),
        "Status": "OPTIMAL",
    })

    # 2. SciPy linear_sum_assignment
    t0 = time.perf_counter()
    r_sp, c_sp = linear_sum_assignment(cost_matrix)
    t_sp = (time.perf_counter() - t0) * 1000
    solver_records.append({
        "Tool / Solver": "SciPy (linear_sum_assignment)",
        "Category": "Operations Research / Hungarian",
        "Optimal Cost (Z)": round(float(cost_matrix[r_sp, c_sp].sum()), 4),
        "Execution Time (ms)": round(t_sp, 3),
        "Status": "OPTIMAL",
    })

    # 3. PuLP (Integer Linear Programming)
    t0 = time.perf_counter()
    pulp_pairs, pulp_cost = solve_with_pulp(cost_matrix, drivers, vehicles)
    t_pulp = (time.perf_counter() - t0) * 1000
    solver_records.append({
        "Tool / Solver": "PuLP (Integer Linear Programming)",
        "Category": "MILP Formulation / CBC Solver",
        "Optimal Cost (Z)": round(pulp_cost, 4),
        "Execution Time (ms)": round(t_pulp, 3),
        "Status": "OPTIMAL",
    })

    # 4. Google OR-Tools
    t0 = time.perf_counter()
    or_pairs, or_cost = solve_with_ortools(cost_matrix, drivers, vehicles)
    t_or = (time.perf_counter() - t0) * 1000
    solver_records.append({
        "Tool / Solver": "Google OR-Tools",
        "Category": "Operations Research / CBC-SCIP",
        "Optimal Cost (Z)": round(or_cost, 4),
        "Execution Time (ms)": round(t_or, 3),
        "Status": "OPTIMAL",
    })

    df_solver_comparison = pd.DataFrame(solver_records)

    # Detailed driver-vehicle pairing schedule
    df_assignment, optimized_cost = solve_assignment(
        cost_matrix, drivers, vehicles, driver_summary, vehicle_summary
    )

    # --------------------------------------------------------------------------
    # PHASE 4: WORKLOAD FAIRNESS & FLEET UTILIZATION ANALYSIS
    # --------------------------------------------------------------------------
    metrics = compute_workload_metrics(driver_summary, optimized_cost)
    vehicle_summary, split_distance, split_trips = compute_vehicle_utilization(vehicle_summary)

    # --------------------------------------------------------------------------
    # PHASE 5: EXPORT ARTIFACTS, EXCEL WORKBOOK, MATLAB MATRIX & VISUAL PLOTS
    # --------------------------------------------------------------------------
    # 1. Export CSV reports
    saved_files = export_pipeline_artifacts(
        df_assignment=df_assignment,
        cost_matrix=cost_matrix,
        drivers=drivers,
        vehicles=vehicles,
        vehicle_summary=vehicle_summary,
        driver_summary=driver_summary,
        output_dir=output_dir,
    )

    # 2. Export Styled Excel Multi-Sheet Workbook
    excel_path = export_excel_workbook(
        df_assignment=df_assignment,
        cost_matrix=cost_matrix,
        drivers=drivers,
        vehicles=vehicles,
        driver_summary=driver_summary,
        vehicle_summary=vehicle_summary,
        solver_comparison=df_solver_comparison,
        output_path=Path("Optimal_Driver_Allocation_Workbook.xlsx"),
    )
    saved_files.append(excel_path)

    # 3. Export MATLAB Matrix (.mat)
    mat_file_path = output_dir / "optimal_driver_data.mat"
    savemat(str(mat_file_path), {
        "CostMatrix": cost_matrix,
        "DriverIDs": drivers,
        "VehicleIDs": vehicles,
        "OptimalCost": optimized_cost,
    })
    saved_files.append(mat_file_path)

    # 4. Generate all Visual Analytics Plots
    saved_plots = generate_all_plots(
        cost_matrix=cost_matrix,
        assignments=h_pairs,
        drivers=drivers,
        vehicles=vehicles,
        solver_comparison=df_solver_comparison,
        driver_summary=driver_summary,
        vehicle_summary=vehicle_summary,
        output_dir=plots_dir,
    )

    # 5. Interactive web dashboard (listed in the console output, written below)
    web_path = Path("web") / "index.html"
    saved_files.append(web_path)

    # Render console dashboard once, capturing it so the web page can replay it
    console_buffer = io.StringIO()
    with redirect_stdout(console_buffer):
        display_dashboard(
            shifts_count=len(shifts),
            trips_count=len(trips),
            avg_shift_dur=avg_shift_dur,
            avg_shift_dist=avg_shift_dist,
            min_trips=int(trips_per_veh.min()),
            max_trips=int(trips_per_veh.max()),
            n_drivers=n_drivers,
            n_vehicles=n_vehicles,
            df_assignment=df_assignment,
            df_solver_comparison=df_solver_comparison,
            metrics=metrics,
            split_distance=split_distance,
            split_trips=split_trips,
            saved_files=saved_files,
            saved_plots=saved_plots,
        )
    console_output = console_buffer.getvalue()
    if verbose:
        print(console_output, end="")

    export_web_dashboard(
        output_path=web_path,
        cost_matrix=cost_matrix,
        drivers=drivers,
        vehicles=vehicles,
        driver_summary=driver_summary,
        vehicle_summary=vehicle_summary,
        df_assignment=df_assignment,
        df_solver_comparison=df_solver_comparison,
        hungarian_trace=hungarian_trace,
        metrics=metrics,
        split_distance=split_distance,
        split_trips=split_trips,
        overview={
            "shifts_count": len(shifts),
            "trips_count": len(trips),
            "avg_shift_dur": avg_shift_dur,
            "avg_shift_dist": avg_shift_dist,
            "min_trips": int(trips_per_veh.min()),
            "max_trips": int(trips_per_veh.max()),
            "n_drivers": n_drivers,
            "n_vehicles": n_vehicles,
        },
        console_output=console_output,
        saved_files=saved_files,
        saved_plots=saved_plots,
    )
    if open_web:
        webbrowser.open(web_path.resolve().as_uri())

    return {
        "assignments": df_assignment,
        "solver_comparison": df_solver_comparison,
        "metrics": metrics,
        "saved_files": saved_files,
        "saved_plots": saved_plots,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Optimal Driver-Vehicle Allocation Decision Support Pipeline"
    )
    parser.add_argument(
        "--shift-data",
        type=Path,
        default=None,
        help="Path to ShiftData.csv (default: data/raw/ShiftData.csv)",
    )
    parser.add_argument(
        "--trip-data",
        type=Path,
        default=None,
        help="Path to TripData.csv (default: data/raw/TripData.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save generated CSV/MAT reports (default: data/processed/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress dashboard terminal output",
    )
    parser.add_argument(
        "--open-web",
        action="store_true",
        help="Open the interactive web dashboard (web/index.html) in a browser",
    )

    args = parser.parse_args()
    run_pipeline(
        shift_path=args.shift_data,
        trip_path=args.trip_data,
        output_dir=args.output_dir,
        verbose=not args.quiet,
        open_web=args.open_web,
    )


if __name__ == "__main__":
    main()
