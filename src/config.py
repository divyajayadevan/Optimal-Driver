from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Input CSV files
DEFAULT_SHIFT_FILE = RAW_DATA_DIR / "ShiftData.csv"
DEFAULT_TRIP_FILE = RAW_DATA_DIR / "TripData.csv"

# Fallback paths for root CSV files
FALLBACK_SHIFT_FILE = PROJECT_ROOT / "ShiftData.csv"
FALLBACK_TRIP_FILE = PROJECT_ROOT / "TripData.csv"

# Output files
OUTPUT_ASSIGNMENT_FILE = PROCESSED_DATA_DIR / "optimal_assignment.csv"
OUTPUT_COST_MATRIX_FILE = PROCESSED_DATA_DIR / "cost_matrix_21x21.csv"
OUTPUT_VEHICLE_UTIL_FILE = PROCESSED_DATA_DIR / "vehicle_utilization.csv"
OUTPUT_DRIVER_SUMMARY_FILE = PROCESSED_DATA_DIR / "driver_summary.csv"

# Multi-Objective Cost Matrix Weights
WEIGHT_DISTANCE = 0.50     # w1: Driver Average Distance factor
WEIGHT_DURATION = 0.30     # w2: Driver Shift Duration factor
WEIGHT_UTILIZATION = 0.20  # w3: Vehicle Utilization factor

# Operational Constraints & Penalties
STATION_MISMATCH_PENALTY = 2.50
DISTANCE_MISMATCH_COEFFICIENT = 0.35
BASE_OFFSET = 0.15

# Baseline Benchmarks
BASELINE_TOTAL_COST = 8.6823
BASELINE_WBI = 0.8400

# Utilization Classification Thresholds
UTILIZATION_BINS = [-float("inf"), 0.50, 0.80, float("inf")]
UTILIZATION_LABELS = ["Low", "Moderate", "High"]
