from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def solve_hungarian_algorithm(
    cost_matrix: np.ndarray, trace: Optional[List[dict]] = None
) -> Tuple[List[Tuple[int, int]], float]:
    """
    Kuhn-Munkres (Hungarian) Algorithm for Bipartite Linear Assignment.
    Guarantees global minimum total assignment cost in polynomial time O(N^3).

    If a `trace` list is passed, a snapshot of every algorithm step (reductions,
    zero-covering lines, theta adjustments, final matching) is appended to it.

    Returns:
        assignments: List of (row_index, col_index)
        total_cost: Float sum of minimal assignment cost
    """
    matrix = np.array(cost_matrix, dtype=float)
    n = matrix.shape[0]
    orig_matrix = matrix.copy()

    def record(step: str, **extra) -> None:
        if trace is not None:
            trace.append({"step": step, "matrix": matrix.round(6).tolist(), **extra})

    record("original")

    # Step 1: Row Reduction
    row_mins = matrix.min(axis=1, keepdims=True)
    matrix -= row_mins
    record("row_reduction", row_mins=row_mins.ravel().tolist())

    # Step 2: Column Reduction
    col_mins = matrix.min(axis=0, keepdims=True)
    matrix -= col_mins
    record("col_reduction", col_mins=col_mins.ravel().tolist())

    # Steps 3 & 4: Line Covering & Matrix Adjustments
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
        record(
            "cover",
            iteration=iteration,
            matching=list(match_row),
            matching_size=matching_size,
            covered_rows=covered_rows,
            covered_cols=covered_cols,
            theta=float(theta),
        )

        for r in range(n):
            for c in range(n):
                if not covered_rows[r] and not covered_cols[c]:
                    matrix[r, c] -= theta
                elif covered_rows[r] and covered_cols[c]:
                    matrix[r, c] += theta

        record(
            "adjust",
            iteration=iteration,
            covered_rows=covered_rows,
            covered_cols=covered_cols,
            theta=float(theta),
        )
        iteration += 1

    assignments = [(r, match_row[r]) for r in range(n)]
    total_cost = sum(orig_matrix[r, match_row[r]] for r in range(n))
    record("optimal", matching=list(match_row), total_cost=float(total_cost))
    return assignments, total_cost


def solve_assignment(
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
    driver_summary: pd.DataFrame,
    vehicle_summary: pd.DataFrame,
) -> Tuple[pd.DataFrame, float]:
    """
    Execute Hungarian assignment and cross-validate with SciPy.
    Returns:
        df_assignment (pd.DataFrame): Detailed pairing table
        optimized_total_cost (float): Total assignment cost
    """
    assignments, optimized_total_cost = solve_hungarian_algorithm(cost_matrix)

    # Cross-verify with SciPy linear_sum_assignment
    r_scipy, c_scipy = linear_sum_assignment(cost_matrix)
    scipy_total = cost_matrix[r_scipy, c_scipy].sum()
    if not np.isclose(optimized_total_cost, scipy_total, atol=1e-4):
        raise ValueError(
            f"Discrepancy detected: Custom Hungarian ({optimized_total_cost:.4f}) vs SciPy ({scipy_total:.4f})"
        )

    allocation_records = []
    for r, c in assignments:
        p_id = drivers[r]
        v_id = vehicles[c]
        d_st = driver_summary.loc[r, "StationCode"]
        v_st = vehicle_summary.loc[c, "StationCode"]
        cell_c = cost_matrix[r, c]
        allocation_records.append({
            "Driver": p_id,
            "AssignedVehicle": v_id,
            "SameStation": (d_st == v_st),
            "CellCost": cell_c,
        })

    df_assignment = pd.DataFrame(allocation_records)
    return df_assignment, optimized_total_cost
