# Optimal Driver-Vehicle Allocation System

An Operations Research Decision-Support System (DSS) utilizing the **Hungarian Algorithm (Kuhn-Munkres)** to optimize public transit fleet scheduling, minimize operational costs, ensure 100% depot alignment, and balance driver workloads.

---

## Project Architecture

```text
optimal_driver/
├── data/
│   ├── raw/
│   │   ├── ShiftData.csv
│   │   └── TripData.csv
│   └── processed/
│       ├── optimal_assignment.csv
│       ├── cost_matrix_21x21.csv
│       ├── vehicle_utilization.csv
│       ├── driver_summary.csv
│       └── optimal_driver_data.mat
├── plots/
│   ├── 1_cost_matrix_assignments_heatmap.png
│   ├── 2_solver_runtime_and_convergence_comparison.png
│   ├── 3_bipartite_allocation_network.png
│   └── 4_workload_and_utilization_distribution.png
├── src/
│   ├── config.py
│   ├── ingestion/
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── modeling/
│   │   ├── cost_matrix.py
│   │   ├── hungarian_solver.py
│   │   └── alternative_solvers.py
│   ├── analytics/
│   │   ├── workload.py
│   │   └── utilization.py
│   └── reporting/
│       ├── console_view.py
│       ├── summary_exporter.py
│       ├── excel_exporter.py
│       └── plotter.py
├── tests/
│   └── test_pipeline.py
├── main.py
├── allocate_drivers.py
├── matlab_assignment_solver.m
├── Optimal_Driver_Allocation_Workbook.xlsx
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Unified Optimization & Analytics Pipeline
One single command executes all 4 optimization solvers (Custom Hungarian, SciPy, PuLP, Google OR-Tools), exports CSVs, generates the styled multi-tab Excel report, exports MATLAB `.mat` matrix data, and renders all 4 publication-grade visual plots:
```bash
python main.py
```

### 3. Run Unit Tests (Optional)
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Performance Benchmarks

| Metric | Baseline | Optimized Output | Operational Impact |
| :--- | :---: | :---: | :--- |
| **Total Assignment Cost ($Z$)** | `8.6823` | **`8.3348`** | **4.00% Cost Reduction** (up to 28.8% on target pairs) |
| **Depot Station Alignment** | Mixed | **100% Matched** | **Zero cross-depot deadheading** across all 3 stations |
| **Workload Balance Index (WBI)** | `0.8400` | **`0.8419`** | Improved fairness; reduces driver fatigue |
| **Fleet Utilization (Distance)** | Uneven | **5 High, 13 Mod, 3 Low** | Clear asset rotation visibility |
| **Execution Time** | Manual hours | **< 0.05s** | Instant polynomial-time global optimum |

---

## Roadmap & Documentation

* **Executive Report:** Full analysis, mathematical formulation, and horizon priorities are in [`Optimal_Driver_Allocation_Comprehensive_Report.pdf`](Optimal_Driver_Allocation_Comprehensive_Report.pdf).
* **Next Steps:**
  1. **Web Dashboard:** Interactive Streamlit/React UI with live depot maps and weight sliders.
  2. **Rostering & Preferences:** Multi-day schedule rostering with driver shift preferences and DOT rest hours.
  3. **Real-Time Telemetry:** Live GPS re-dispatching and EV battery charging management.