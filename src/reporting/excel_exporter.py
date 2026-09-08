"""
Excel Exporter for Optimal Driver-Vehicle Allocation Pipeline.
Generates a styled, multi-sheet .xlsx workbook.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def export_excel_workbook(
    df_assignment: pd.DataFrame,
    cost_matrix: np.ndarray,
    drivers: np.ndarray,
    vehicles: np.ndarray,
    driver_summary: pd.DataFrame,
    vehicle_summary: pd.DataFrame,
    solver_comparison: pd.DataFrame,
    output_path: Path = Path("Optimal_Driver_Allocation_Workbook.xlsx"),
) -> Path:
    """
    Export all allocation results, cost matrices, workload metrics, and solver comparisons
    to a styled Excel (.xlsx) workbook using xlsxwriter.
    """
    output_path = Path(output_path)
    
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        
        # Color palettes & formatting styles
        header_fmt = workbook.add_format({
            "bold": True,
            "font_name": "Calibri",
            "font_size": 11,
            "font_color": "#FFFFFF",
            "bg_color": "#1B365D",  # Navy
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })
        
        cell_center = workbook.add_format({"align": "center", "valign": "vcenter"})
        cell_currency = workbook.add_format({"num_format": "0.0000", "align": "right"})
        cell_match_yes = workbook.add_format({"bg_color": "#D4EDDA", "font_color": "#155724", "align": "center"})
        
        # 1. Optimal Assignments Sheet
        df_assignment.to_excel(writer, sheet_name="Optimal_Assignments", index=False)
        ws_assign = writer.sheets["Optimal_Assignments"]
        ws_assign.set_column("A:D", 18, cell_center)
        ws_assign.set_row(0, 24, header_fmt)
        
        # 2. Solver Benchmarks Sheet
        solver_comparison.to_excel(writer, sheet_name="Solver_Comparison", index=False)
        ws_solv = writer.sheets["Solver_Comparison"]
        ws_solv.set_column("A:E", 22, cell_center)
        ws_solv.set_row(0, 24, header_fmt)
        
        # 3. Cost Matrix Sheet
        df_cost = pd.DataFrame(
            cost_matrix,
            index=[f"Pilot_{d}" for d in drivers],
            columns=[f"Veh_{v}" for v in vehicles],
        )
        df_cost.to_excel(writer, sheet_name="Cost_Matrix")
        ws_cost = writer.sheets["Cost_Matrix"]
        ws_cost.set_column(0, len(vehicles), 12, cell_currency)
        ws_cost.set_row(0, 22, header_fmt)
        
        # Add 3-color conditional heatmap formatting to Cost Matrix
        ws_cost.conditional_format(1, 1, len(drivers), len(vehicles), {
            "type": "3_color_scale",
            "min_color": "#63BE7B",  # Green (low cost)
            "mid_color": "#FFEB84",  # Yellow
            "max_color": "#F8696B",  # Red (high cost)
        })
        
        # 4. Driver & Vehicle Summaries
        driver_summary.to_excel(writer, sheet_name="Driver_Workload", index=False)
        ws_d = writer.sheets["Driver_Workload"]
        ws_d.set_column("A:H", 16, cell_center)
        ws_d.set_row(0, 22, header_fmt)
        
        vehicle_summary.to_excel(writer, sheet_name="Vehicle_Utilization", index=False)
        ws_v = writer.sheets["Vehicle_Utilization"]
        ws_v.set_column("A:H", 16, cell_center)
        ws_v.set_row(0, 22, header_fmt)
        
    return output_path
