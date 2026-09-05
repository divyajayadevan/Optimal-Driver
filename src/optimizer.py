"""
Optimization Engine Module.
Formulates the multi-criteria cost matrix and solves the Linear Sum Assignment Problem (LSAP)
using the Hungarian (Kuhn-Munkres) Algorithm.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


@dataclass
class AssignmentResult:
    assignments: List[Tuple[int, int]]  # (row_idx, col_idx) pairs
    driver_ids: List[int]
    vehicle_ids: List[int]
    costs: List[float]
    total_cost: float
    iterations: int
    matched_matrix: np.ndarray


class CostMatrixBuilder:
    """Builds a multi-objective cost matrix for driver-vehicle pairings."""

    def __init__(
        self,
        driver_profiles: pd.DataFrame,
        vehicle_profiles: pd.DataFrame,
        w1: float = 0.4,
        w2: float = 0.3,
        w3: float = 0.3,
        depot_penalty: float = 45.0,
        wear_weight: float = 0.4
    ):
        self.driver_profiles = driver_profiles
        self.vehicle_profiles = vehicle_profiles
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.depot_penalty = depot_penalty
        self.wear_weight = wear_weight

    def build(self) -> Tuple[np.ndarray, List[int], List[int]]:
        """Constructs an N x N cost matrix matching active drivers to vehicles."""
        drivers = self.driver_profiles['Pilotcode'].values
        vehicles = self.vehicle_profiles['VehicleCode'].values
        n = min(len(drivers), len(vehicles))

        drivers = drivers[:n]
        vehicles = vehicles[:n]

        cost_matrix = np.zeros((n, n), dtype=float)

        for i in range(n):
            d_row = self.driver_profiles.iloc[i]
            d_dist = d_row['Avg_Distance']
            d_time = d_row['Avg_Duration']
            d_station = d_row['Primary_Station']

            for j in range(n):
                v_row = self.vehicle_profiles.iloc[j]
                v_dist = v_row['Avg_Distance']
                v_station = v_row['Primary_Station']

                # Deadhead penalty for cross-depot dispatch
                station_penalty = 0.0 if d_station == v_station else self.depot_penalty
                
                # Wear balancing penalty
                wear_penalty = abs(d_dist - v_dist) * self.wear_weight

                # Multi-objective cost formula
                c_ij = (self.w1 * d_dist) + (self.w2 * d_time * 8.0) + (self.w3 * v_dist) + station_penalty + wear_penalty
                cost_matrix[i, j] = c_ij

        return cost_matrix, list(drivers), list(vehicles)


class HungarianOptimizer:
    """
    Step-by-step Kuhn-Munkres (Hungarian) Algorithm Solver.
    Solves bipartite matching in polynomial time O(N^3) guaranteeing global optimality.
    """

    def __init__(
        self,
        cost_matrix: np.ndarray,
        row_labels: Optional[List[str]] = None,
        col_labels: Optional[List[str]] = None,
        verbose: bool = False
    ):
        self.original_matrix = np.array(cost_matrix, dtype=float)
        self.n = self.original_matrix.shape[0]
        assert self.original_matrix.shape[0] == self.original_matrix.shape[1], "Cost matrix must be square (N x N)."
        
        self.row_labels = row_labels if row_labels else [f"Driver_{i+1}" for i in range(self.n)]
        self.col_labels = col_labels if col_labels else [f"Vehicle_{j+1}" for j in range(self.n)]
        self.verbose = verbose

    def _format_matrix(self, matrix: np.ndarray, covered_rows=None, covered_cols=None) -> str:
        col_w = max(9, max(len(str(c)) for c in self.col_labels) + 2)
        row_w = max(len(str(r)) for r in self.row_labels) + 2

        lines = []
        header = " " * row_w + " | " + " | ".join(f"{str(c):>{col_w}}" for c in self.col_labels)
        lines.append(header)
        lines.append("-" * len(header))

        for i in range(self.n):
            row_prefix = f"{str(self.row_labels[i]):<{row_w}}"
            row_tag = " [L]" if covered_rows and covered_rows[i] else "    "
            row_vals = []
            for j in range(self.n):
                val_str = f"{matrix[i, j]:.2f}"
                if matrix[i, j] == 0:
                    val_str = f"({val_str})"
                row_vals.append(f"{val_str:>{col_w}}")
            lines.append(f"{row_prefix}{row_tag} | " + " | ".join(row_vals))

        if covered_cols and any(covered_cols):
            col_cov_str = " " * (row_w + 4) + " | " + " | ".join(
                f"{'[^LINE^]':>{col_w}}" if covered_cols[j] else f"{' ':>{col_w}}" for j in range(self.n)
            )
            lines.append(col_cov_str)

        return "\n".join(lines)

    def solve(self) -> AssignmentResult:
        """Executes all 5 steps of the Hungarian Algorithm."""
        matrix = self.original_matrix.copy()
        n = self.n

        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 0: INITIAL COST MATRIX")
            print("=" * 80)
            print(self._format_matrix(matrix))

        # STEP 1: Row Reduction
        row_mins = matrix.min(axis=1, keepdims=True)
        matrix -= row_mins

        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 1: ROW REDUCTION (Subtracting minimum element from each row)")
            print("=" * 80)
            print(self._format_matrix(matrix))

        # STEP 2: Column Reduction
        col_mins = matrix.min(axis=0, keepdims=True)
        matrix -= col_mins

        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 2: COLUMN REDUCTION (Subtracting minimum element from each column)")
            print("=" * 80)
            print(self._format_matrix(matrix))

        # STEP 3 & 4: Covering Zeros & Matrix Adjustments (Iterative)
        iteration = 1
        match_row = [-1] * n

        while True:
            zeros = (matrix == 0)
            match_col = [-1] * n
            match_row = [-1] * n

            def dfs(u: int, visited: List[bool]) -> bool:
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
                if self.verbose:
                    print(f"\nSTEP 3: Optimal Assignment Found! (Matching size = {n} / {n})")
                break

            # Find minimum line cover using Kőnig's theorem
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
            num_lines = sum(covered_rows) + sum(covered_cols)

            if self.verbose:
                print(f"\nSTEP 3 (Iteration {iteration}): Covering Lines = {num_lines} / {n}")
                print(self._format_matrix(matrix, covered_rows, covered_cols))

            # STEP 4: Cost Shift
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

        # STEP 5: Assemble Final Assignment
        assignments = [(r, match_row[r]) for r in range(n)]
        costs = [float(self.original_matrix[r, match_row[r]]) for r in range(n)]
        total_cost = float(sum(costs))

        # Verification against SciPy
        r_scipy, c_scipy = linear_sum_assignment(self.original_matrix)
        scipy_total = float(self.original_matrix[r_scipy, c_scipy].sum())
        assert np.isclose(total_cost, scipy_total), f"Hungarian cost {total_cost} != SciPy cost {scipy_total}"

        return AssignmentResult(
            assignments=assignments,
            driver_ids=[int(self.row_labels[r].replace("Driver_", "").replace("Pilot_", "")) if "Driver_" in self.row_labels[r] or "Pilot_" in self.row_labels[r] else r for r in range(n)],
            vehicle_ids=[int(self.col_labels[match_row[r]].replace("Vehicle_", "").replace("Veh_", "")) if "Vehicle_" in self.col_labels[match_row[r]] or "Veh_" in self.col_labels[match_row[r]] else match_row[r] for r in range(n)],
            costs=costs,
            total_cost=total_cost,
            iterations=iteration,
            matched_matrix=matrix
        )
