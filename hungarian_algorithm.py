"""
================================================================================
HUNGARIAN ALGORITHM (KUHN-MUNKRES ALGORITHM) - STEP-BY-STEP SOLVER
================================================================================
This module implements the Hungarian Algorithm from scratch with clear, 
step-by-step pedagogical explanations and visual matrix outputs.

The Hungarian algorithm solves the Linear Assignment Problem (bipartite matching)
in polynomial time O(N^3), guaranteeing a global minimum total cost.
"""

from typing import List, Tuple, Dict, Any
import numpy as np


class HungarianSolver:
    """
    Step-by-step implementation of the Hungarian (Kuhn-Munkres) Algorithm.
    Provides detailed intermediate matrix snapshots, line covering visualizations,
    and mathematical explanations for every stage of the algorithm.
    """

    def __init__(self, cost_matrix: np.ndarray, row_labels=None, col_labels=None, verbose: bool = True):
        self.original_matrix = np.array(cost_matrix, dtype=float)
        self.n = self.original_matrix.shape[0]
        assert self.original_matrix.shape[0] == self.original_matrix.shape[1], "Matrix must be square (N x N)."
        
        self.row_labels = row_labels if row_labels is not None else [f"Driver_{i+1}" for i in range(self.n)]
        self.col_labels = col_labels if col_labels is not None else [f"Vehicle_{j+1}" for j in range(self.n)]
        self.verbose = verbose
        self.history: List[Dict[str, Any]] = []

    def _format_matrix(self, matrix: np.ndarray, covered_rows=None, covered_cols=None) -> str:
        """Pretty formats an N x N matrix with row and column headers and line indicators."""
        col_w = max(9, max(len(str(c)) for c in self.col_labels) + 2)
        row_w = max(len(str(r)) for r in self.row_labels) + 2
        
        lines = []
        # Header row
        header = " " * row_w + " | " + " | ".join(f"{str(c):>{col_w}}" for c in self.col_labels)
        sep = "-" * len(header)
        lines.append(header)
        lines.append(sep)
        
        for i in range(self.n):
            row_prefix = f"{str(self.row_labels[i]):<{row_w}}"
            # Add indicator if row is covered
            row_tag = " [L]" if covered_rows and covered_rows[i] else "    "
            row_vals = []
            for j in range(self.n):
                val_str = f"{matrix[i, j]:.2f}"
                if matrix[i, j] == 0:
                    val_str = f"({val_str})"  # Highlight zeros
                row_vals.append(f"{val_str:>{col_w}}")
            lines.append(f"{row_prefix}{row_tag} | " + " | ".join(row_vals))
            
        if covered_cols and any(covered_cols):
            col_cov_str = " " * (row_w + 4) + " | " + " | ".join(
                f"{'[^LINE^]':>{col_w}}" if covered_cols[j] else f"{' ':>{col_w}}" for j in range(self.n)
            )
            lines.append(col_cov_str)
            
        return "\n".join(lines)

    def solve(self) -> Tuple[List[Tuple[int, int]], float]:
        """
        Executes all 5 steps of the Hungarian Algorithm.
        
        Returns:
            assignments: List of (row_idx, col_idx) optimal pairs.
            total_cost: The sum of costs from the original cost matrix.
        """
        matrix = self.original_matrix.copy()
        n = self.n

        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 0: INITIAL COST MATRIX")
            print("=" * 80)
            print("Each cell C[i, j] represents the operational cost of assigning Driver i to Vehicle j.")
            print(self._format_matrix(matrix))

        # ----------------------------------------------------------------------
        # STEP 1: ROW REDUCTION
        # ----------------------------------------------------------------------
        # Subtract the minimum element in each row from all elements in that row.
        # This creates at least one zero in every row without changing the optimal assignment.
        row_mins = matrix.min(axis=1, keepdims=True)
        matrix -= row_mins
        
        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 1: ROW REDUCTION (Subtract minimum element of each row)")
            print("=" * 80)
            print("Row minimums subtracted:")
            for i, r_min in enumerate(row_mins.flatten()):
                print(f"  - {self.row_labels[i]}: min = {r_min:.2f}")
            print("\nMatrix after Row Reduction (zeros in parentheses):")
            print(self._format_matrix(matrix))

        # ----------------------------------------------------------------------
        # STEP 2: COLUMN REDUCTION
        # ----------------------------------------------------------------------
        # Subtract the minimum element in each column from all elements in that column.
        # This ensures every column has at least one zero.
        col_mins = matrix.min(axis=0, keepdims=True)
        matrix -= col_mins
        
        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 2: COLUMN REDUCTION (Subtract minimum element of each column)")
            print("=" * 80)
            print("Column minimums subtracted:")
            for j, c_min in enumerate(col_mins.flatten()):
                print(f"  - {self.col_labels[j]}: min = {c_min:.2f}")
            print("\nMatrix after Column Reduction (zeros in parentheses):")
            print(self._format_matrix(matrix))

        # ----------------------------------------------------------------------
        # STEP 3 & 4: COVERING ZEROS AND MATRIX ADJUSTMENTS (ITERATIVE)
        # ----------------------------------------------------------------------
        iteration = 1
        match_row = [-1] * n

        while True:
            if self.verbose:
                print("\n" + "=" * 80)
                print(f"STEP 3 (Iteration {iteration}): COVER ZEROS WITH MINIMUM HORIZONTAL/VERTICAL LINES")
                print("=" * 80)

            # Maximum Bipartite Matching on Zero entries
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

            if self.verbose:
                print(f"Current maximum number of non-conflicting (independent) zeros: {matching_size} / {n}")

            # By Kőnig's theorem: Min lines to cover all zeros == Max matching size of zeros
            if matching_size == n:
                if self.verbose:
                    print(f"--> Found {n} independent zeros! Exactly {n} lines are needed (equals matrix dimension).")
                    print("--> An optimal assignment is achievable directly using the zero cells!")
                break

            # Find minimum vertex cover (lines) using standard bipartite graph reduction
            # 1. Mark unmatched rows
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

            # Lines covering all zeros are: Unmarked Rows + Marked Columns
            covered_rows = [not marked_rows[r] for r in range(n)]
            covered_cols = [marked_cols[c] for c in range(n)]
            num_lines = sum(covered_rows) + sum(covered_cols)

            if self.verbose:
                cov_r_names = [self.row_labels[i] for i, v in enumerate(covered_rows) if v]
                cov_c_names = [self.col_labels[j] for j, v in enumerate(covered_cols) if v]
                print(f"Minimum lines required: {num_lines} (Covered Rows: {cov_r_names}, Covered Cols: {cov_c_names})")
                print(f"Since lines ({num_lines}) < matrix size ({n}), we must adjust the matrix.")
                print("\nMatrix with covering lines marked ([L] = Covered Row, [^LINE^] = Covered Column):")
                print(self._format_matrix(matrix, covered_rows, covered_cols))

            # ------------------------------------------------------------------
            # STEP 4: MATRIX ADJUSTMENT (Cost Shift)
            # ------------------------------------------------------------------
            uncovered_mask = np.zeros((n, n), dtype=bool)
            for r in range(n):
                for c in range(n):
                    if not covered_rows[r] and not covered_cols[c]:
                        uncovered_mask[r, c] = True

            theta = matrix[uncovered_mask].min()
            if self.verbose:
                print("\n" + "-" * 80)
                print(f"STEP 4: SHIFT COSTS BY SMALLEST UNCOVERED VALUE (theta = {theta:.2f})")
                print("-" * 80)
                print(f"  1. Subtract theta ({theta:.2f}) from all uncovered elements.")
                print(f"  2. Add theta ({theta:.2f}) to all intersection elements (covered by BOTH a row line and col line).")
                print("  3. Leave singly covered elements unchanged.")

            # Apply theta transformation
            for r in range(n):
                for c in range(n):
                    if not covered_rows[r] and not covered_cols[c]:
                        matrix[r, c] -= theta
                    elif covered_rows[r] and covered_cols[c]:
                        matrix[r, c] += theta

            if self.verbose:
                print("\nAdjusted Cost Matrix for next iteration:")
                print(self._format_matrix(matrix))

            iteration += 1

        # ----------------------------------------------------------------------
        # STEP 5: FINAL OPTIMAL ASSIGNMENT
        # ----------------------------------------------------------------------
        assignments = [(r, match_row[r]) for r in range(n)]
        total_cost = sum(self.original_matrix[r, c] for r, c in assignments)

        if self.verbose:
            print("\n" + "=" * 80)
            print("STEP 5: OPTIMAL ALLOCATION ASSIGNMENT")
            print("=" * 80)
            print(f"{'Driver':<25} -> {'Assigned Vehicle':<25} | {'Cost':>10}")
            print("-" * 65)
            for r, c in assignments:
                cost_val = self.original_matrix[r, c]
                print(f"{self.row_labels[r]:<25} -> {self.col_labels[c]:<25} | {cost_val:>10.2f}")
            print("-" * 65)
            print(f"{'TOTAL OPTIMIZED OPERATIONAL COST:':<53} {total_cost:>10.2f}")
            print("=" * 80)

        return assignments, total_cost


def run_pedagogical_examples():
    """Demonstrates Hungarian Algorithm on classic benchmark matrices."""
    print("\n" + "#" * 80)
    print("# DEMO 1: 3x3 Problem from Project Presentation (Slide 7)")
    print("#" * 80)
    slide_matrix = np.array([
        [15.0, 18.0, 20.0],
        [10.0, 14.0, 16.0],
        [12.0, 17.0, 13.0]
    ])
    solver3 = HungarianSolver(
        slide_matrix,
        row_labels=["Driver D1", "Driver D2", "Driver D3"],
        col_labels=["Vehicle V1", "Vehicle V2", "Vehicle V3"]
    )
    solver3.solve()

    print("\n\n" + "#" * 80)
    print("# DEMO 2: 4x4 Multi-Iteration Problem with Line Covering & Matrix Adjustments")
    print("#" * 80)
    mat_4x4 = np.array([
        [90.0, 75.0, 75.0, 80.0],
        [35.0, 85.0, 55.0, 65.0],
        [125.0, 95.0, 90.0, 105.0],
        [45.0, 110.0, 95.0, 115.0]
    ])
    solver4 = HungarianSolver(
        mat_4x4,
        row_labels=["Driver D1", "Driver D2", "Driver D3", "Driver D4"],
        col_labels=["Vehicle V1", "Vehicle V2", "Vehicle V3", "Vehicle V4"]
    )
    solver4.solve()


if __name__ == "__main__":
    run_pedagogical_examples()
