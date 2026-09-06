import unittest
import numpy as np
import pandas as pd

from src.ingestion.loader import load_shift_data, load_trip_data
from src.ingestion.preprocessor import summarize_drivers, summarize_vehicles
from src.modeling.cost_matrix import build_cost_matrix
from src.modeling.hungarian_solver import solve_hungarian_algorithm, solve_assignment
from src.analytics.workload import compute_workload_metrics
from src.analytics.utilization import compute_vehicle_utilization


class TestOptimalDriverPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shifts = load_shift_data()
        cls.trips = load_trip_data()

    def test_01_ingestion(self):
        self.assertEqual(len(self.shifts), 491, "Should ingest exactly 491 shift records")
        self.assertTrue(len(self.trips) > 0, "Trip records should not be empty")
        self.assertIn("Duration_Hours", self.shifts.columns)

    def test_02_preprocessing(self):
        driver_summary = summarize_drivers(self.shifts)
        vehicle_summary = summarize_vehicles(self.shifts, self.trips)
        self.assertEqual(len(driver_summary), 21, "Driver pool size must be 21")
        self.assertEqual(len(vehicle_summary), 21, "Vehicle pool size must be 21")

    def test_03_cost_matrix_dimensions(self):
        driver_summary = summarize_drivers(self.shifts)
        vehicle_summary = summarize_vehicles(self.shifts, self.trips)
        cost_matrix, drivers, vehicles = build_cost_matrix(driver_summary, vehicle_summary)
        self.assertEqual(cost_matrix.shape, (21, 21), "Cost matrix must be 21x21")

    def test_04_hungarian_solver(self):
        driver_summary = summarize_drivers(self.shifts)
        vehicle_summary = summarize_vehicles(self.shifts, self.trips)
        cost_matrix, drivers, vehicles = build_cost_matrix(driver_summary, vehicle_summary)
        df_assignment, total_cost = solve_assignment(
            cost_matrix, drivers, vehicles, driver_summary, vehicle_summary
        )
        self.assertEqual(len(df_assignment), 21)
        self.assertEqual(len(df_assignment["Driver"].unique()), 21, "Each driver must be uniquely assigned")
        self.assertEqual(len(df_assignment["AssignedVehicle"].unique()), 21, "Each vehicle must be uniquely assigned")
        self.assertTrue(np.isclose(total_cost, 8.3348, atol=1e-3), f"Total cost expected ~8.3348, got {total_cost}")

    def test_05_analytics(self):
        driver_summary = summarize_drivers(self.shifts)
        vehicle_summary = summarize_vehicles(self.shifts, self.trips)
        metrics = compute_workload_metrics(driver_summary, 8.3348)
        self.assertGreater(metrics["wbi"], 0.84, "WBI must exceed baseline 0.84")
        self.assertGreater(metrics["cost_reduction_pct"], 3.5, "Cost reduction should be positive")

        _, split_dist, split_trips = compute_vehicle_utilization(vehicle_summary)
        self.assertEqual(split_dist.sum(), 21)
        self.assertEqual(split_trips.sum(), 21)


if __name__ == "__main__":
    unittest.main()
