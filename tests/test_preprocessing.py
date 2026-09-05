"""
Unit tests for data preprocessing and ingestion pipeline using standard unittest.
"""

import unittest
import pandas as pd
import numpy as np

from src.preprocessing import DataIngestionPipeline, DatasetSummary


class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        self.pipeline = DataIngestionPipeline()

    def test_data_ingestion_loads_shift_data(self):
        df = self.pipeline.load_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 491)
        self.assertIn("Duration_Hours", df.columns)
        self.assertTrue((df["Duration_Hours"] >= 0).all())

    def test_aggregate_profiles(self):
        driver_stats, vehicle_stats = self.pipeline.aggregate_profiles()
        self.assertEqual(len(driver_stats), 21)
        self.assertEqual(len(vehicle_stats), 21)
        self.assertIn("Avg_Distance", driver_stats.columns)
        self.assertIn("Primary_Station", driver_stats.columns)
        self.assertTrue(set(driver_stats["Primary_Station"].unique()).issubset({503, 504, 511}))

    def test_dataset_summary(self):
        summary = self.pipeline.get_summary()
        self.assertIsInstance(summary, DatasetSummary)
        self.assertEqual(summary.total_records, 491)
        self.assertEqual(summary.num_drivers, 21)
        self.assertEqual(summary.num_vehicles, 21)
        self.assertEqual(summary.num_stations, 3)
        self.assertTrue(np.isclose(summary.avg_shift_distance, 116.97, atol=0.5))


if __name__ == "__main__":
    unittest.main()
