# Optimal Driver-Vehicle Allocation System

An Operations Research Decision-Support System (DSS) utilizing the **Hungarian Algorithm (Kuhn-Munkres)** to optimize public transit fleet scheduling, minimize operational costs, ensure 100% depot alignment, and balance driver workloads.

---

## 📁 Project Architecture

```text
optimal_driver/
├── data/
│   ├── raw/                           # ShiftData.csv (491 shifts) & TripData.csv (11,352 trips)
│   └── processed/                     # Generated schedules, cost matrix & utilization CSVs
├── src/
│   ├── config.py                      # Multi-objective weights (w1=0.5, w2=0.3, w3=0.2) & paths
│   ├── ingestion/                     # Data cleaning, timestamp parsing & driver/vehicle profiling
│   ├── modeling/                      # 21x21 Cost matrix builder & Hungarian solver O(N³)
│   ├── analytics/                     # Workload variance (σ²), WBI & fleet utilization
│   └── reporting/                     # Dashboard display & CSV report exporter
├── tests/                             # Automated unit test suite (100% pass)
├── main.py                            # CLI pipeline entrypoint
├── generate_report_pdf.py             # 3-page comprehensive PDF report generator
├── Optimal_Driver_Allocation_Comprehensive_Report.pdf
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Optimization Pipeline
```bash
python main.py
```

### 3. Run Unit Tests & PDF Report Generator
```bash
python -m unittest discover -s tests -p "test_*.py"
python generate_report_pdf.py
```

---

## 📊 Performance Benchmarks

| Metric | Baseline | Optimized Output | Operational Impact |
| :--- | :---: | :---: | :--- |
| **Total Assignment Cost ($Z$)** | `8.6823` | **`8.3348`** | **4.00% Cost Reduction** (up to 28.8% on target pairs) |
| **Depot Station Alignment** | Mixed | **100% Matched** | **Zero cross-depot deadheading** across all 3 stations |
| **Workload Balance Index (WBI)** | `0.8400` | **`0.8419`** | Improved fairness; reduces driver fatigue |
| **Fleet Utilization (Distance)** | Uneven | **5 High, 13 Mod, 3 Low** | Clear asset rotation visibility |
| **Execution Time** | Manual hours | **< 0.05s** | Instant polynomial-time global optimum |

---

## 🗺️ Roadmap & Documentation

* **Executive Report:** Full analysis, mathematical formulation, and horizon priorities are in [`Optimal_Driver_Allocation_Comprehensive_Report.pdf`](Optimal_Driver_Allocation_Comprehensive_Report.pdf).
* **Next Steps:**
  1. **Web Dashboard:** Interactive Streamlit/React UI with live depot maps and weight sliders.
  2. **Rostering & Preferences:** Multi-day schedule rostering with driver shift preferences and DOT rest hours.
  3. **Real-Time Telemetry:** Live GPS re-dispatching and EV battery charging management.