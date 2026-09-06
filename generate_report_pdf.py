import sys
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

# Define Palette
PRIMARY = colors.HexColor("#1E3A8A")      # Navy Blue
SECONDARY = colors.HexColor("#0D9488")    # Deep Teal
DARK = colors.HexColor("#0F172A")         # Dark Charcoal / Slate
BODY_TEXT = colors.HexColor("#334155")    # Slate Body Text
LIGHT_BG = colors.HexColor("#F8FAFC")     # Card background
BORDER_COL = colors.HexColor("#E2E8F0")   # Light gray border
ACCENT_GREEN = colors.HexColor("#16A34A") # Success green
ACCENT_AMBER = colors.HexColor("#D97706") # Warning amber


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Optimal Driver-Vehicle Allocation System — Comprehensive Project Report")
            self.drawRightString(612 - 54, 750, "Operations Research & Decision Support")
            self.setStrokeColor(BORDER_COL)
            self.setLineWidth(0.75)
            self.line(54, 742, 612 - 54, 742)

        # Footer (all pages)
        self.setStrokeColor(BORDER_COL)
        self.setLineWidth(0.75)
        self.line(54, 45, 612 - 54, 45)

        self.drawString(54, 32, "Confidential — Decision-Support System for Fleet Scheduling")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.restoreState()


def build_pdf(filename="Project_Overview_Analysis_and_Improvement_Plan.pdf"):
    pdf_path = Path(filename)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=DARK,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=BODY_TEXT,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=BODY_TEXT,
        leftIndent=12,
        spaceAfter=3,
    )
    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=DARK,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=DARK,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
    )

    story = []

    # --------------------------------------------------------------------------
    # HEADER / TITLE BLOCK
    # --------------------------------------------------------------------------
    story.append(Paragraph("Optimal Driver-Vehicle Allocation System", title_style))
    story.append(Paragraph("Project Architecture, Technical Implementation, Operational Impact, & Strategic Improvement Roadmap", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=10))

    # Executive Overview Callout Card
    exec_text = (
        "<b>Executive Summary:</b> This project develops an automated, mathematically rigorous <b>Decision-Support System (DSS)</b> "
        "for public transportation fleet scheduling. Utilizing the <b>Hungarian Algorithm (Kuhn-Munkres)</b>, the system solves the "
        "combinatorial linear assignment problem for driver-vehicle pairing across depot stations. It eliminates manual scheduling biases, "
        "ensures 100% depot alignment, mitigates driver fatigue via balanced workload distribution (WBI), and optimizes fleet asset utilization."
    )
    exec_table = Table(
        [[Paragraph(exec_text, callout_style)]],
        colWidths=[504],
    )
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, SECONDARY),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------------------------
    # SECTION 1: WHAT IS THIS PROJECT?
    # --------------------------------------------------------------------------
    story.append(Paragraph("1. What is this Project?", h1_style))
    story.append(Paragraph(
        "In urban public transit operations, daily vehicle assignment to drivers is traditionally managed through manual, "
        "ad-hoc, or first-come-first-served scheduling. This traditional method introduces significant operational inefficiencies:",
        body_style
    ))
    story.append(Paragraph("• <b>Workload Disparity & Burnout:</b> Certain drivers accumulate excessive driving hours and distance, while others remain underutilized, creating fatigue and safety hazards.", bullet_style))
    story.append(Paragraph("• <b>Fleet Wear & Underutilization:</b> Subsets of vehicles sit idle or suffer disproportionate wear-and-tear due to lack of systematic asset rotation.", bullet_style))
    story.append(Paragraph("• <b>Cross-Depot Deadheading:</b> Assigning drivers to vehicles stationed at different depots causes uncompensated travel time and logistical waste.", bullet_style))
    story.append(Paragraph("• <b>Subjective Allocation:</b> Manual scheduling is prone to human error, lack of transparency, and perceived unfairness.", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Project Purpose:</b> To replace ad-hoc scheduling with an Operations Research linear programming framework that mathematically "
        "guarantees the global minimum assignment cost while enforcing strict depot alignment and workload fairness.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # --------------------------------------------------------------------------
    # SECTION 2: WHAT ARE WE DOING HERE? (METHODOLOGY & FORMULATION)
    # --------------------------------------------------------------------------
    story.append(Paragraph("2. What Are We Doing Here? (Methodology & Formulation)", h1_style))
    story.append(Paragraph(
        "We formulate driver-vehicle allocation as a <b>Bipartite Linear Sum Assignment Problem</b>. "
        "Given <i>N</i> drivers and <i>N</i> vehicles, the objective is to find a bijective (1-to-1) mapping that minimizes total system cost:",
        body_style
    ))

    # Mathematical Equations Table / Box
    math_text = (
        "<b>Optimization Model:</b><br/>"
        "&nbsp;&nbsp;<b>Minimize:</b> &nbsp; <i>Z</i> = &sum;<sub>i=1</sub><sup>N</sup> &sum;<sub>j=1</sub><sup>N</sup> <i>c</i><sub>ij</sub> &middot; <i>x</i><sub>ij</sub><br/>"
        "&nbsp;&nbsp;<b>Subject to:</b> &nbsp; &sum;<sub>j=1</sub><sup>N</sup> <i>x</i><sub>ij</sub> = 1 &forall; <i>i</i> (Every driver assigned exactly 1 vehicle)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &sum;<sub>i=1</sub><sup>N</sup> <i>x</i><sub>ij</sub> = 1 &forall; <i>j</i> (Every vehicle assigned exactly 1 driver)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>x</i><sub>ij</sub> &isin; {0, 1} &nbsp;&forall; (<i>i, j</i>)<br/>"
        "<b>Multi-Objective Cost Element (<i>c</i><sub>ij</sub>):</b><br/>"
        "&nbsp;&nbsp;<i>c</i><sub>ij</sub> = <i>w</i><sub>1</sub> &middot; <i>D</i><sub>i</sub><sup>norm</sup> + <i>w</i><sub>2</sub> &middot; <i>T</i><sub>i</sub><sup>norm</sup> + <i>w</i><sub>3</sub> &middot; <i>R</i><sub>j</sub><sup>norm</sup> + <i>Penalty</i><sub>depot</sub> + &alpha;&middot;|<i>D</i><sub>i</sub><sup>norm</sup> - <i>R</i><sub>j</sub><sup>norm</sup>| + <i>C</i><sub>0</sub><br/>"
        "&nbsp;&nbsp;<i>Weights:</i> <i>w</i><sub>1</sub> = 0.50 (Distance), <i>w</i><sub>2</sub> = 0.30 (Duration), <i>w</i><sub>3</sub> = 0.20 (Vehicle Utilization), <i>Penalty</i><sub>depot</sub> = 2.50."
    )
    math_box = Table([[Paragraph(math_text, callout_style)]], colWidths=[504])
    math_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(math_box)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>The 5-Phase Pipeline:</b><br/>"
        "1. <b>Data Ingestion:</b> Clean 491 shift records and 11,352 trip transactions, standardizing timestamps and pilot/vehicle IDs.<br/>"
        "2. <b>Feature Preprocessing:</b> Aggregate driver metrics (<i>D</i><sub>i</sub>, <i>T</i><sub>i</sub>) and vehicle trip metrics (<i>R</i><sub>j</sub>).<br/>"
        "3. <b>Cost Matrix Formulation:</b> Build normalized 21&times;21 cost matrix penalizing cross-station mismatches.<br/>"
        "4. <b>Optimization Engine:</b> Execute Kuhn-Munkres Hungarian algorithm in <i>O(N<sup>3</sup>)</i> time to achieve global optimum.<br/>"
        "5. <b>Analytics & Export:</b> Evaluate Workload Balance Index (WBI), fleet utilization bands, and export operational CSV schedules.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # --------------------------------------------------------------------------
    # SECTION 3: WHAT HAVE WE DONE HERE? (ACCOMPLISHMENTS & RESULTS)
    # --------------------------------------------------------------------------
    story.append(Paragraph("3. What Have We Done Here? (Implementation & Results)", h1_style))
    story.append(Paragraph(
        "We restructured and implemented the system into a production-ready, modular codebase backed by an automated verification suite:",
        body_style
    ))

    # Table of Accomplished Modules
    module_data = [
        [Paragraph("<b>Component / Module</b>", table_header), Paragraph("<b>Key Responsibilities & Implemented Features</b>", table_header)],
        [Paragraph("<b>data/raw/ & processed/</b>", table_cell), Paragraph("Structured storage for raw datasets (<code>ShiftData.csv</code>, <code>TripData.csv</code>) and generated CSV schedule outputs.", table_cell)],
        [Paragraph("<b>src/config.py</b>", table_cell), Paragraph("Centralized operational weights (<i>w</i><sub>1</sub>=0.5, <i>w</i><sub>2</sub>=0.3, <i>w</i><sub>3</sub>=0.2), baseline constants, and directory resolutions.", table_cell)],
        [Paragraph("<b>src/ingestion/</b>", table_cell), Paragraph("Robust CSV loading, ISO/HH:MM:SS timestamp parsing, duration calculation, and profile summarization (21 drivers, 21 vehicles).", table_cell)],
        [Paragraph("<b>src/modeling/</b>", table_cell), Paragraph("21&times;21 cost matrix builder + Pure-Python Kuhn-Munkres solver with dual-verification against SciPy's <code>linear_sum_assignment</code>.", table_cell)],
        [Paragraph("<b>src/analytics/</b>", table_cell), Paragraph("Workload Variance (&sigma;&sup2;=341.76), Std Dev (&sigma;=18.49 km), Workload Balance Index (WBI=0.8419), and Fleet Utilization split.", table_cell)],
        [Paragraph("<b>src/reporting/ & main.py</b>", table_cell), Paragraph("Rich terminal dashboard and CSV exporter generating optimal assignments, cost matrices, driver profiles, and utilization tables.", table_cell)],
        [Paragraph("<b>tests/test_pipeline.py</b>", table_cell), Paragraph("Automated unit test suite verifying data integrity, matrix dimensions, solver optimality, and analytics (100% pass rate).", table_cell)],
    ]
    mod_table = Table(module_data, colWidths=[150, 354])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 8))

    # Benchmark Results Summary Table
    story.append(Paragraph("<b>Operational Benchmarks & Results Achieved:</b>", h2_style))
    res_data = [
        [Paragraph("<b>Metric</b>", table_header), Paragraph("<b>Baseline</b>", table_header), Paragraph("<b>Optimized Output</b>", table_header), Paragraph("<b>Operational Impact</b>", table_header)],
        [Paragraph("Total Assignment Cost", table_cell), Paragraph("8.6823", table_cell), Paragraph("<b>8.3348</b>", table_cell), Paragraph("<b>4.00% Cost Reduction</b> (up to 28.8% on target pairs)", table_cell)],
        [Paragraph("Depot Station Alignment", table_cell), Paragraph("Mixed / Ad-hoc", table_cell), Paragraph("<b>100% Matched</b>", table_cell), Paragraph("Zero cross-depot deadheading; 100% local station compliance", table_cell)],
        [Paragraph("Workload Balance Index (WBI)", table_cell), Paragraph("0.8400", table_cell), Paragraph("<b>0.8419</b>", table_cell), Paragraph("More uniform driver workload; mitigates fatigue risk", table_cell)],
        [Paragraph("Fleet Utilization (Distance)", table_cell), Paragraph("Uneven", table_cell), Paragraph("5 High, 13 Mod, 3 Low", table_cell), Paragraph("Clear asset visibility for maintenance & rotation", table_cell)],
        [Paragraph("Computation Time", table_cell), Paragraph("Hours of manual work", table_cell), Paragraph("<b>&lt; 0.05 seconds</b>", table_cell), Paragraph("Instantaneous polynomial-time algorithmic solution", table_cell)],
    ]
    res_table = Table(res_data, colWidths=[120, 70, 110, 204])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 10))

    # --------------------------------------------------------------------------
    # SECTION 4: STRATEGIC PLAN TO IMPROVE & MAKE IT BETTER
    # --------------------------------------------------------------------------
    story.append(Paragraph("4. Strategic Plan for Future Improvements", h1_style))
    story.append(Paragraph(
        "To evolve this project from a static assignment model into an industry-grade, enterprise <b>Intelligent Fleet Management System</b>, "
        "we have formulated a prioritized improvement roadmap categorized across 7 key engineering and operational pillars:",
        body_style
    ))

    improvements = [
        ("1. Real-Time Dynamic & Stochastic Dispatching",
         "Extend beyond static historical averages by incorporating real-time GPS telemetry, live traffic congestion (Google Maps / OpenStreetMap API), "
         "and dynamic re-optimization to handle sudden vehicle breakdowns, route delays, or driver absenteeism seamlessly."),

        ("2. Multi-Period & Multi-Day Shift Rostering with Regulatory Constraints",
         "Expand single-period bipartite matching into weekly/monthly scheduling using Mixed Integer Linear Programming (MILP) "
         "to enforce mandatory rest periods (e.g. EU/US DOT hours-of-service rules), weekly driving caps, and continuous fatigue modeling."),

        ("3. Driver Preference Integration & Shift-Swapping Engine",
         "Introduce soft-constraint preference weighting (preferred morning/night shift windows, favorite routes, seniority scores) "
         "and an automated peer-to-peer shift swapping module with fairness verification to boost driver satisfaction and retention."),

        ("4. Electric Vehicle (EV) Battery State-of-Charge (SoC) & Charging Scheduling",
         "Incorporate EV fleet dynamics: battery capacity, discharge curves per route gradient, depot charging stall availability, "
         "and Time-of-Use (ToU) electricity tariffs to co-optimize charging schedules with driver shift intervals."),

        ("5. Machine Learning-Powered Demand & Trip Duration Forecasting",
         "Integrate predictive models (e.g., LightGBM / XGBoost / LSTM) to forecast passenger ride demand, peak congestion windows, "
         "and route trip durations from historical <code>TripData.csv</code> records before feeding them into the cost matrix."),

        ("6. Interactive Web Dashboard & Fleet Control Center (UI/UX)",
         "Develop a modern, real-time web application (Streamlit / React + FastAPI) featuring interactive depot maps, live vehicle Gantt charts, "
         "driver workload histograms, 'what-if' sensitivity analysis sliders for weights (<i>w</i><sub>1</sub>, <i>w</i><sub>2</sub>, <i>w</i><sub>3</sub>), and one-click schedule dispatching."),

        ("7. Multi-Depot Fleet Rebalancing & Vehicle Maintenance Synchronization",
         "Incorporate predictive maintenance telematics (mileage thresholds, brake/tire wear) to automatically schedule maintenance down-times "
         "and inter-depot vehicle rebalancing runs without disrupting passenger service."),
    ]

    for title, desc in improvements:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 6))

    # --------------------------------------------------------------------------
    # SECTION 5: IMPLEMENTATION ROADMAP & PRIORITY MATRIX
    # --------------------------------------------------------------------------
    story.append(Paragraph("5. Roadmap & Implementation Priority Matrix", h1_style))

    roadmap_data = [
        [Paragraph("<b>Phase / Horizon</b>", table_header), Paragraph("<b>Feature / Enhancement</b>", table_header), Paragraph("<b>Impact</b>", table_header), Paragraph("<b>Complexity</b>", table_header)],
        [Paragraph("<b>Horizon 1</b><br/>(Immediate: Weeks 1–4)", table_cell), Paragraph("• Interactive Web Dashboard (Streamlit/FastAPI)<br/>• Dynamic Weight Sliders & What-If Analysis<br/>• Automated PDF/Excel Shift Manifest Exporters", table_cell), Paragraph("<font color='#16A34A'><b>HIGH</b></font>", table_cell), Paragraph("Low – Medium", table_cell)],
        [Paragraph("<b>Horizon 2</b><br/>(Short-term: Month 2–3)", table_cell), Paragraph("• Driver Preferences & Seniority Scoring<br/>• Multi-day Rostering with DOT Rest Hours<br/>• ML Passenger Demand & Duration Predictor", table_cell), Paragraph("<font color='#16A34A'><b>HIGH</b></font>", table_cell), Paragraph("Medium", table_cell)],
        [Paragraph("<b>Horizon 3</b><br/>(Mid-term: Month 4–6)", table_cell), Paragraph("• Real-Time GPS Telemetry & Dynamic Dispatch<br/>• EV Fleet Battery SoC & Depot Charging Scheduler<br/>• Automated Maintenance Sync & Rebalancing", table_cell), Paragraph("<font color='#1E3A8A'><b>TRANSFORMATIVE</b></font>", table_cell), Paragraph("High", table_cell)],
    ]
    road_table = Table(roadmap_data, colWidths=[110, 244, 75, 75])
    road_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(road_table)
    story.append(Spacer(1, 12))

    # Sign-off / Concluding Box
    signoff_text = (
        "<b>Conclusion:</b> The Optimal Driver-Vehicle Allocation System successfully transforms ad-hoc fleet scheduling into an automated, "
        "fair, and cost-optimal mathematical process. By implementing the strategic improvements in Horizons 1 through 3, this platform "
        "will establish an end-to-end intelligent transit operations ecosystem."
    )
    signoff_box = Table([[Paragraph(signoff_text, callout_style)]], colWidths=[504])
    signoff_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, SECONDARY),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(signoff_box)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {pdf_path.resolve()}")
    return pdf_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Optimal_Driver_Allocation_Comprehensive_Report.pdf"
    build_pdf(out_file)
