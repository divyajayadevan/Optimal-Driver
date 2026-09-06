"""
================================================================================
OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM
================================================================================
Command-Line Interface / Decision-Support Pipeline for Public Transport Fleets.
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding in Windows shells
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.ingestion.loader import load_shift_data, load_trip_data
from src.ingestion.preprocessor import summarize_drivers, summarize_vehicles
from src.modeling.cost_matrix import build_cost_matrix
from src.modeling.hungarian_solver import solve_assignment
from src.analytics.workload import compute_workload_metrics
from src.analytics.utilization import compute_vehicle_utilization
from src.reporting.summary_exporter import export_pipeline_artifacts
from src.reporting.console_view import display_dashboard


def run_pipeline(
    shift_path: Path = None,
    trip_path: Path = None,
    output_dir: Path = None,
    verbose: bool = True,
):
    """
    Execute full 5-phase optimization workflow.
    """
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
    # PHASE 3: MATHEMATICAL OPTIMIZATION (HUNGARIAN ALGORITHM)
    # --------------------------------------------------------------------------
    df_assignment, optimized_cost = solve_assignment(
        cost_matrix, drivers, vehicles, driver_summary, vehicle_summary
    )

    # --------------------------------------------------------------------------
    # PHASE 4: WORKLOAD FAIRNESS & FLEET UTILIZATION ANALYSIS
    # --------------------------------------------------------------------------
    metrics = compute_workload_metrics(driver_summary, optimized_cost)
    vehicle_summary, split_distance, split_trips = compute_vehicle_utilization(vehicle_summary)

    # --------------------------------------------------------------------------
    # PHASE 5: DECISION-SUPPORT REPORTING & ARTIFACT EXPORT
    # --------------------------------------------------------------------------
    saved_files = export_pipeline_artifacts(
        df_assignment=df_assignment,
        cost_matrix=cost_matrix,
        drivers=drivers,
        vehicles=vehicles,
        vehicle_summary=vehicle_summary,
        driver_summary=driver_summary,
        output_dir=output_dir,
    )

    if verbose:
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
            metrics=metrics,
            split_distance=split_distance,
            split_trips=split_trips,
            saved_files=saved_files,
        )

    return {
        "assignments": df_assignment,
        "metrics": metrics,
        "saved_files": saved_files,
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
        help="Directory to save generated CSV reports (default: data/processed/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress dashboard terminal output",
    )

    args = parser.parse_args()
    run_pipeline(
        shift_path=args.shift_data,
        trip_path=args.trip_data,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
