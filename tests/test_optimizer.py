"""
Unit tests for the Hungarian Optimizer and Cost Matrix Builder using standard unittest.
"""

import unittest
import numpy as np
from scipy.optimize import linear_sum_assignment

from src.optimizer import CostMatrixBuilder, HungarianOptimizer
from src.preprocessing import DataIngestionPipeline


class TestOptimizer(unittest.TestCase):

    def test_hungarian_3x3_slide_example(self):
        matrix = np.array([
            [15.0, 18.0, 20.0],
            [10.0, 14.0, 16.0],
            [12.0, 17.0, 13.0]
        ])
        solver = HungarianOptimizer(matrix)
        result = solver.solve()
        self.assertEqual(result.total_cost, 41.0)
        self.assertEqual(set(result.assignments), {(0, 1), (1, 0), (2, 2)})

    def test_hungarian_4x4_multi_iteration(self):
        matrix = np.array([
            [90.0, 75.0, 75.0, 80.0],
            [35.0, 85.0, 55.0, 65.0],
            [125.0, 95.0, 90.0, 105.0],
            [45.0, 110.0, 95.0, 115.0]
        ])
        solver = HungarianOptimizer(matrix)
        result = solver.solve()
        
        r_ind, c_ind = linear_sum_assignment(matrix)
        scipy_cost = matrix[r_ind, c_ind].sum()
        self.assertEqual(result.total_cost, scipy_cost)
        self.assertEqual(result.total_cost, 275.0)

    def test_cost_matrix_builder_and_fleet_optimization(self):
        pipeline = DataIngestionPipeline()
        d_stats, v_stats = pipeline.aggregate_profiles()
        builder = CostMatrixBuilder(d_stats, v_stats)
        cost_matrix, drivers, vehicles = builder.build()

        self.assertEqual(cost_matrix.shape, (21, 21))
        self.assertTrue((cost_matrix > 0).all())

        solver = HungarianOptimizer(cost_matrix)
        result = solver.solve()
        self.assertEqual(len(result.assignments), 21)

        # 1-to-1 constraint check
        rows = [r for r, c in result.assignments]
        cols = [c for r, c in result.assignments]
        self.assertEqual(len(set(rows)), 21)
        self.assertEqual(len(set(cols)), 21)


if __name__ == "__main__":
    unittest.main()
