"""
Alternative Optimization Solvers for Driver-Vehicle Allocation:
- PuLP: Linear Programming / MIP formulation
- Google OR-Tools: Linear Sum Assignment & Mixed Integer Programming
- MATLAB script exporter for matrix computation and validation
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import pulp
from ortools.linear_solver import pywraplp


def solve_with_pulp(
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
) -> Tuple[List[Tuple[int, int]], float]:
    """
    Solve Driver-Vehicle Allocation using PuLP Integer Linear Programming (ILP).
    
    Formulation:
      Minimize: sum_{i} sum_{j} C_{ij} * X_{ij}
      Subject to:
        sum_{j} X_{ij} = 1  for all drivers i
        sum_{i} X_{ij} = 1  for all vehicles j
        X_{ij} in {0, 1}
    """
    n = len(drivers)
    prob = pulp.LpProblem("Driver_Vehicle_Allocation", pulp.LpMinimize)
    
    # Binary decision variables
    x = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat=pulp.LpBinary)
        for i in range(n)
        for j in range(n)
    }
    
    # Objective function
    prob += pulp.lpSum(cost_matrix[i, j] * x[(i, j)] for i in range(n) for j in range(n))
    
    # Constraint 1: Every driver is assigned exactly one vehicle
    for i in range(n):
        prob += pulp.lpSum(x[(i, j)] for j in range(n)) == 1, f"Driver_Assign_{i}"
        
    # Constraint 2: Every vehicle is assigned to exactly one driver
    for j in range(n):
        prob += pulp.lpSum(x[(i, j)] for i in range(n)) == 1, f"Vehicle_Assign_{j}"
        
    # Solve with default CBC solver (silent)
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    assignments = []
    total_cost = 0.0
    for i in range(n):
        for j in range(n):
            if pulp.value(x[(i, j)]) > 0.5:
                assignments.append((i, j))
                total_cost += cost_matrix[i, j]
                
    return assignments, total_cost


def solve_with_ortools(
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
) -> Tuple[List[Tuple[int, int]], float]:
    """
    Solve Driver-Vehicle Allocation using Google OR-Tools Linear Solver.
    """
    n = len(drivers)
    solver = pywraplp.Solver.CreateSolver("CBC")
    if not solver:
        solver = pywraplp.Solver.CreateSolver("SCIP")
        
    # Variables
    x = {}
    for i in range(n):
        for j in range(n):
            x[i, j] = solver.IntVar(0, 1, f"x_{i}_{j}")
            
    # Objective
    objective = solver.Objective()
    for i in range(n):
        for j in range(n):
            objective.SetCoefficient(x[i, j], float(cost_matrix[i, j]))
    objective.SetMinimization()
    
    # Each driver gets exactly 1 vehicle
    for i in range(n):
        constraint = solver.RowConstraint(1, 1, f"driver_{i}")
        for j in range(n):
            constraint.SetCoefficient(x[i, j], 1)
            
    # Each vehicle gets exactly 1 driver
    for j in range(n):
        constraint = solver.RowConstraint(1, 1, f"vehicle_{j}")
        for i in range(n):
            constraint.SetCoefficient(x[i, j], 1)
            
    status = solver.Solve()
    
    assignments = []
    total_cost = 0.0
    if status == pywraplp.Solver.OPTIMAL:
        for i in range(n):
            for j in range(n):
                if x[i, j].solution_value() > 0.5:
                    assignments.append((i, j))
                    total_cost += cost_matrix[i, j]
                    
    return assignments, total_cost
