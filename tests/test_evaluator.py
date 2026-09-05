"""
Unit tests for the Evaluation and Analytics module using standard unittest.
"""

import unittest
import numpy as np
import pandas as pd

from src.evaluator import AllocationEvaluator
from src.optimizer import CostMatrixBuilder, HungarianOptimizer
from src.preprocessing import DataIngestionPipeline


class TestEvaluator(unittest.TestCase):

    def test_wbi_calculation(self):
        # Uniform workloads -> WBI = 1.0
        series_uniform = pd.Series([100.0, 100.0, 100.0, 100.0])
        self.assertEqual(AllocationEvaluator.calculate_wbi(series_uniform), 1.0)

        # Variable workloads
        series_var = pd.Series([80.0, 100.0, 120.0])
        mean = 100.0
        std = np.std([80.0, 100.0, 120.0], ddof=0)
        expected_wbi = 1.0 - (std / mean)
        self.assertTrue(np.isclose(AllocationEvaluator.calculate_wbi(series_var), expected_wbi))

    def test_evaluation_pipeline(self):
        pipeline = DataIngestionPipeline()
        d_stats, v_stats = pipeline.aggregate_profiles()
        builder = CostMatrixBuilder(d_stats, v_stats)
        cost_matrix, drivers, vehicles = builder.build()

        solver = HungarianOptimizer(cost_matrix)
        result = solver.solve()

        evaluator = AllocationEvaluator(d_stats, v_stats, cost_matrix, result)
        metrics = evaluator.evaluate()

        self.assertLess(metrics.optimized_cost, metrics.baseline_cost)
        self.assertGreater(metrics.cost_reduction_pct, 20.0)
        self.assertEqual(metrics.depot_alignment_pct, 100.0)
        self.assertTrue(np.isclose(metrics.baseline_wbi, 0.84, atol=0.01))

        df_alloc = evaluator.generate_allocation_dataframe()
        self.assertEqual(len(df_alloc), 21)
        self.assertIn("Assignment_Cost", df_alloc.columns)


if __name__ == "__main__":
    unittest.main()
