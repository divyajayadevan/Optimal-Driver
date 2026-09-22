# Optimal Driver-Vehicle Allocation System

An Operations Research Decision-Support System (DSS) utilizing **Combinatorial Optimization & Linear Programming** (Kuhn-Munkres Hungarian Algorithm, SciPy, PuLP, and Google OR-Tools) to optimize public transit fleet scheduling, minimize operational costs, ensure 100% depot alignment, and balance driver workloads.

---

## Key Highlights

- **Multi-Solver Engine**: Cross-validated across **4 optimization engines** (Custom Kuhn-Munkres Hungarian, SciPy, PuLP MILP, Google OR-Tools) with 100% mathematical convergence to the global optimum ($Z = 8.3348$).
- **100% Depot Alignment**: Zero cross-depot deadhead trips across Station 503, Station 504, and Station 511.
- **Fairness & Balance**: Improved Workload Balance Index (WBI) to $0.8419$ while achieving a **4.00% operational cost reduction**.
- **Automated Reporting & Visuals**: Single-command execution generates multi-sheet styled Excel workbooks, MATLAB matrix validation files, and 4 publication-grade visual analytics plots.

---

## Project Architecture

```text
optimal_driver/
├── data/
│   ├── raw/
│   │   ├── ShiftData.csv                     # Historical shift durations & distances
│   │   └── TripData.csv                      # Vehicle trip-level operational telemetry
│   └── processed/
│       ├── optimal_assignment.csv            # Optimized 21x21 driver-vehicle pairings
│       ├── cost_matrix_21x21.csv             # Full normalized bipartite cost matrix
│       ├── vehicle_utilization.csv           # Vehicle asset utilization tiers
│       ├── driver_summary.csv                # Driver workload summary profiles
│       └── optimal_driver_data.mat           # MATLAB-compatible matrix export
├── plots/
│   ├── 1_cost_matrix_assignments_heatmap.png # Cost matrix heatmap with marked optimal pairs
│   ├── 2_solver_runtime_and_convergence_comparison.png # Solver runtime & convergence benchmarks
│   ├── 3_bipartite_allocation_network.png    # Depot-color-coded bipartite matching graph
│   └── 4_workload_and_utilization_distribution.png # Workload histograms & utilization scatter
├── src/
│   ├── config.py                             # Optimization weights & penalty constants
│   ├── ingestion/
│   │   ├── loader.py                         # Shift and trip data ingestion loaders
│   │   └── preprocessor.py                   # Aggregation & driver/vehicle profiling
│   ├── modeling/
│   │   ├── cost_matrix.py                    # Multi-objective cost matrix builder
│   │   ├── hungarian_solver.py               # Kuhn-Munkres O(N^3) solver & SciPy validation
│   │   └── alternative_solvers.py            # PuLP (ILP) and Google OR-Tools solvers
│   ├── analytics/
│   │   ├── workload.py                       # Workload Balance Index (WBI) & variance
│   │   └── utilization.py                    # Fleet asset utilization classification
│   └── reporting/
│       ├── console_view.py                   # Clean terminal UI dashboard
│       ├── summary_exporter.py               # CSV artifact exporter
│       ├── excel_exporter.py                 # Multi-sheet styled Excel (.xlsx) generator
│       └── plotter.py                        # Matplotlib visual analytics generator
├── tests/
│   └── test_pipeline.py                      # Automated unit test suite
├── main.py                                   # Master unified pipeline entry point
├── allocate_drivers.py                       # Backward-compatibility execution wrapper
├── matlab_assignment_solver.m                # Standalone MATLAB validation & plotting script
├── Optimal_Driver_Allocation_Workbook.xlsx   # Formatted Excel workbook with heatmaps
├── requirements.txt                          # Project Python dependencies
└── README.md                                 # Documentation
```

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Unified Pipeline
Execute the full 5-phase optimization workflow, solver benchmarking, Excel report creation, MATLAB matrix export, and plot generation with a single command:
```bash
python main.py
```

#### Optional CLI Arguments
```bash
python main.py --shift-data path/to/ShiftData.csv --trip-data path/to/TripData.csv --output-dir data/processed/ --quiet
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Mathematical Formulation

The driver-vehicle allocation is modeled as a **Bipartite Minimum Weight Perfect Matching** (Linear Sum Assignment) problem:

$$\min Z = \sum_{i=1}^{N} \sum_{j=1}^{N} C_{ij} \cdot X_{ij}$$

$$\text{subject to: } \sum_{j=1}^{N} X_{ij} = 1 \quad \forall i \in \{1, \dots, N\} \quad (\text{Each driver assigned exactly 1 vehicle})$$

$$\sum_{i=1}^{N} X_{ij} = 1 \quad \forall j \in \{1, \dots, N\} \quad (\text{Each vehicle assigned exactly 1 driver})$$

$$X_{ij} \in \{0, 1\} \quad \forall i, j$$

### Cost Matrix Construction ($C_{ij}$)
Each cell cost combines normalized distance, shift duration, vehicle utilization, and hard depot constraints:
$$C_{ij} = w_1 \cdot \bar{D}_i + w_2 \cdot \bar{T}_i + w_3 \cdot \bar{R}_j + P_{\text{station}} + P_{\text{diff}}$$

Where:
- $\bar{D}_i, \bar{T}_i$: Normalized driver distance and shift duration.
- $\bar{R}_j$: Normalized vehicle distance utilization.
- $P_{\text{station}}$: Station mismatch penalty ($0$ if same depot, $1.5$ if cross-depot).
- $P_{\text{diff}}$: Driver-vehicle distance disparity coefficient ($0.3 \cdot |\bar{D}_i - \bar{R}_j|$).

---

## Solver Benchmarking

| Optimization Solver | Formulation / Paradigm | Optimal Cost ($Z$) | Runtime (ms) | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Python (Kuhn-Munkres)** | Custom Bipartite Graph Matching | **`8.3348`** | `~0.10 ms` | `[OPTIMAL]` |
| **SciPy (`linear_sum_assignment`)** | Operations Research Hungarian | **`8.3348`** | `~0.02 ms` | `[OPTIMAL]` |
| **PuLP (Integer Linear Programming)** | Binary Integer MILP / CBC Solver | **`8.3348`** | `~65 ms` | `[OPTIMAL]` |
| **Google OR-Tools** | Linear Solver / CBC-SCIP Engine | **`8.3348`** | `~12 ms` | `[OPTIMAL]` |

---

## Operational Performance Impact

| Metric | Baseline Fleet | Optimized System | Operational Impact |
| :--- | :---: | :---: | :--- |
| **Total Assignment Cost ($Z$)** | `8.6823` | **`8.3348`** | **4.00% Net Cost Reduction** |
| **Depot Station Alignment** | Mixed | **100% Matched** | **Zero deadhead trips** across all 3 stations |
| **Workload Balance Index (WBI)** | `0.8400` | **`0.8419`** | Improved fairness; mitigates driver fatigue |
| **Fleet Asset Utilization** | Uneven | **5 High, 13 Mod, 3 Low** | Clear wear-and-tear rotation visibility |
| **Execution Speed** | Manual scheduling | **< 0.15s** | Instant global optimum for real-time dispatch |

---

## Generated Deliverables

1. **Terminal Decision Dashboard**: Clean text-based reporting showing solver benchmarks, allocation pairings, and fleet metrics.
2. **Styled Excel Workbook** ([`Optimal_Driver_Allocation_Workbook.xlsx`](Optimal_Driver_Allocation_Workbook.xlsx)):
   - Multi-tab workbook with conditional 3-color heatmap formatting for cost matrices and pairings.
3. **Visual Analytics Suite** ([`plots/`](plots/)):
   - `1_cost_matrix_assignments_heatmap.png`: Matrix heatmap with optimal match points.
   - `2_solver_runtime_and_convergence_comparison.png`: Solver comparison charts.
   - `3_bipartite_allocation_network.png`: Bipartite network diagram color-coded by depot station.
   - `4_workload_and_utilization_distribution.png`: Driver workload & asset utilization profiles.
4. **MATLAB Matrix & Solver** ([`matlab_assignment_solver.m`](matlab_assignment_solver.m) & [`data/processed/optimal_driver_data.mat`](data/processed/optimal_driver_data.mat)):
   - Standalone MATLAB validation script with built-in plotting (`imagesc`, `bar`).