# Optimal Driver-Vehicle Allocation System

An Operations Research linear assignment model using the **Hungarian Algorithm (Kuhn-Munkres)** to optimize public transportation fleet scheduling, minimize operational costs, and balance driver workloads across depot stations.

---

## Project Structure

- `ShiftData.csv`: Historical shift logs across 21 drivers, 21 vehicles, and 3 depot stations (503, 504, 511).
- `TripData.csv`: High-resolution GPS trip transactions and fare records.
- `Driver_Vehicle_Allocation_Presentation.pdf`: Project presentation with research objectives and mathematical formulation.
- `allocate_drivers.py`: Self-contained optimization script implementing the Hungarian Algorithm from scratch with step-by-step trace and full fleet optimization.
- `requirements.txt`: Python package dependencies.

---

## Setup & Execution

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the optimization**:
   ```bash
   python allocate_drivers.py
   ```

---

## Results & Impact

- **Cost Reduction (CR)**: ~28.88% reduction in operational assignment costs.
- **Depot Alignment**: 100% station-aligned allocation (zero cross-depot deadhead miles).
- **Workload Balance**: Optimized distribution minimizing driver fatigue and equalizing vehicle wear.
- **Verification**: Output strictly verified against SciPy's `linear_sum_assignment`.