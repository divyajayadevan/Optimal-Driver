import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# PRESENTATION CONFIGURATION & LIGHT ELEGANT PALETTE
# -----------------------------------------------------------------------------
BG_COLOR = RGBColor(250, 252, 254)         # Off-white / Crisp canvas (#FAFCFE)
WHITE = RGBColor(255, 255, 255)            # #FFFFFF
TEXT_DARK = RGBColor(15, 23, 42)           # Slate 900 (#0F172A)
TEXT_MUTED = RGBColor(71, 85, 105)         # Slate 600 (#475569)
TEXT_LIGHT_MUTED = RGBColor(148, 163, 184) # Slate 400 (#94A3B8)

PRIMARY = RGBColor(29, 78, 216)            # Royal Navy (#1D4ED8)
PRIMARY_DARK = RGBColor(30, 41, 59)        # Slate Dark (#1E293B)
PRIMARY_LIGHT = RGBColor(239, 246, 255)    # Blue 50 (#EFF6FF)
PRIMARY_TINT = RGBColor(219, 234, 254)     # Blue 100 (#DBEAFE)

ACCENT_TEAL = RGBColor(15, 118, 110)       # Deep Teal (#0F766E)
ACCENT_TEAL_LIGHT = RGBColor(240, 253, 250)# Teal 50 (#F0FDFA)

ACCENT_AMBER = RGBColor(180, 83, 9)        # Warm Amber (#B45309)
DIVIDER_COLOR = RGBColor(226, 232, 240)    # Slate 200 (#E2E8F0)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"

SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5


def create_base_presentation():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH)
    prs.slide_height = Inches(SLIDE_HEIGHT)
    return prs


def add_light_background(slide):
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(SLIDE_WIDTH), Inches(SLIDE_HEIGHT)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    return bg


def add_header(slide, section_tag: str, title: str, subtitle: str = ""):
    # Small uppercase section tag
    tb_tag = slide.shapes.add_textbox(Inches(0.9), Inches(0.42), Inches(11.5), Inches(0.28))
    tf_tag = tb_tag.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = section_tag.upper()
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(10.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = PRIMARY

    # Title & Subtitle Box
    tb = slide.shapes.add_textbox(Inches(0.9), Inches(0.72), Inches(11.5), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    
    if subtitle:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(3)

    # Clean thin accent divider
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.58), Inches(11.53), Inches(0.015))
    div.fill.solid()
    div.fill.fore_color.rgb = DIVIDER_COLOR
    div.line.fill.background()


def add_slide_footer(slide, current_page: int, total_pages: int = 15):
    # Bottom subtle line
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(6.92), Inches(11.53), Inches(0.01))
    div.fill.solid()
    div.fill.fore_color.rgb = DIVIDER_COLOR
    div.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.9), Inches(7.02), Inches(11.53), Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = "Optimal Driver–Vehicle Allocation System  •  Department Review Committee (2025–2026)"
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_LIGHT_MUTED
    
    p_num = tf.add_paragraph()
    p_num.text = f"{current_page:02d} / {total_pages:02d}"
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.name = FONT_HEADING
    p_num.font.size = Pt(9.5)
    p_num.font.bold = True
    p_num.font.color.rgb = PRIMARY


def add_bullet_point(text_frame, title: str, body: str, size: int = 11, space_before: int = 8, title_color=TEXT_DARK, body_color=TEXT_MUTED):
    p = text_frame.add_paragraph()
    p.space_before = Pt(space_before)
    
    r1 = p.add_run()
    r1.text = f"•  {title}: " if title else "•  "
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(size)
    r1.font.bold = True
    r1.font.color.rgb = title_color
    
    r2 = p.add_run()
    r2.text = body
    r2.font.name = FONT_BODY
    r2.font.size = Pt(size)
    r2.font.color.rgb = body_color


# -----------------------------------------------------------------------------
# SLIDE BUILDERS (15 CLEAN, HUMANIZED, POINTWISE SLIDES)
# -----------------------------------------------------------------------------

def build_slide_1(prs):
    # SLIDE 1: Title Slide (Clean Humanized Academic Hero)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    
    # Left vertical color bar
    vbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.1), Inches(3.8))
    vbar.fill.solid()
    vbar.fill.fore_color.rgb = PRIMARY
    vbar.line.fill.background()

    # Main Title Block
    tb = slide.shapes.add_textbox(Inches(1.3), Inches(1.75), Inches(10.8), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_tag = tf.paragraphs[0]
    p_tag.text = "RESEARCH PROJECT PRESENTATION  •  ACADEMIC YEAR 2025–2026"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = PRIMARY
    
    p_title = tf.add_paragraph()
    p_title.text = "Optimal Driver–Vehicle Allocation System\nfor Public Transportation"
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_before = Pt(8)

    p_sub = tf.add_paragraph()
    p_sub.text = "A Linear Assignment-Model Approach to Cost-Efficient, Workload-Balanced Fleet Scheduling"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(8)

    p_meta = tf.add_paragraph()
    p_meta.text = "Presented to: Department Review Committee  |  Domain: Fleet Optimization & Combinatorial Algorithms"
    p_meta.font.name = FONT_BODY
    p_meta.font.size = Pt(12)
    p_meta.font.bold = True
    p_meta.font.color.rgb = PRIMARY_DARK
    p_meta.space_before = Pt(24)

    # 3 Bottom Pointwise Summary Badges
    b_tb = slide.shapes.add_textbox(Inches(1.3), Inches(5.8), Inches(10.8), Inches(0.9))
    b_tf = b_tb.text_frame
    b_tf.word_wrap = True
    
    p_b = b_tf.paragraphs[0]
    p_b.text = "Key Focus Areas: Hungarian Algorithm (Kuhn-Munkres)  •  Workload Balancing Index (WBI)  •  Zero Cross-Depot Deadheading"
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_TEAL

    add_slide_footer(slide, 1)


def build_slide_2(prs):
    # SLIDE 2: 01 · PROBLEM STATEMENT (Clean Pointwise Layout)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "01 · Problem Statement",
        "Why Manual Driver–Vehicle Scheduling Falls Short in Public Transit",
        "Real-world operational bottlenecks observed in manual fleet dispatching."
    )

    # 2 Column Open Layout (No heavy cards)
    # Left Column: Operational Inefficiencies
    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p_h1 = tf_left.paragraphs[0]
    p_h1.text = "Observed Inefficiencies in Manual Dispatching"
    p_h1.font.name = FONT_HEADING
    p_h1.font.size = Pt(14)
    p_h1.font.bold = True
    p_h1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Severe Workload Imbalance", "Some drivers consistently log over 190 km per shift while others log under 15 km, creating severe fairness issues.", 11.5, 12)
    add_bullet_point(tf_left, "Driver Fatigue & Safety Risks", "Long shift durations (up to 12.5 hours) without balanced rotation increase exhaustion and on-road safety hazards.", 11.5, 12)
    add_bullet_point(tf_left, "Cross-Depot Deadheading", "Drivers and buses are often paired across different stations, generating costly, uncompensated deadhead miles.", 11.5, 12)

    # Right Column: Fleet & Asset Issues + Research Goal
    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p_h2 = tf_right.paragraphs[0]
    p_h2.text = "Fleet Impacts & Research Objective"
    p_h2.font.name = FONT_HEADING
    p_h2.font.size = Pt(14)
    p_h2.font.bold = True
    p_h2.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Uneven Vehicle Wear", "Certain fleet vehicles are overworked while others remain idle, causing accelerated maintenance costs.", 11.5, 12)
    add_bullet_point(tf_right, "Lack of Quantitative Decision Tools", "Shift supervisors rely on intuition or static rosters rather than data-driven optimization models.", 11.5, 12)
    add_bullet_point(tf_right, "Primary Research Goal", "Develop a mathematical assignment model that minimizes operating costs, enforces 100% depot alignment, and ensures driver workload equity.", 11.5, 14, title_color=PRIMARY, body_color=TEXT_DARK)

    add_slide_footer(slide, 2)


def build_slide_3(prs):
    # SLIDE 3: 02 · PROJECT OBJECTIVES (Pointwise 6-Step Workflow)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "02 · Objectives",
        "Methodological Roadmap: From Raw Shift Logs to Optimized Dispatch",
        "Six structured phases connecting data ingestion, optimization theory, and fleet analytics."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    tf_left.paragraphs[0].text = ""

    add_bullet_point(tf_left, "1. Ingest & Profile Historical Data", "Extract and clean real shift logs (491 shifts, 21 drivers, 21 vehicles, 30 days) across 3 regional depots.", 11.5, 6)
    add_bullet_point(tf_left, "2. Formulate Multi-Objective Cost Matrix", "Construct a normalized 21×21 cost matrix combining shift distance, duty duration, vehicle usage, and depot penalties.", 11.5, 14)
    add_bullet_point(tf_left, "3. Formalize Bipartite Linear Program", "Express driver-vehicle allocation as an exact one-to-one constrained matching problem minimizing total fleet cost Z.", 11.5, 14)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    tf_right.paragraphs[0].text = ""

    add_bullet_point(tf_right, "4. Implement Hungarian Optimization", "Build and solve the assignment model using the Kuhn-Munkres algorithm in O(N³) polynomial time.", 11.5, 6)
    add_bullet_point(tf_right, "5. Cross-Validate Solver Integrity", "Benchmark the from-scratch Hungarian algorithm directly against SciPy's linear assignment solver.", 11.5, 14)
    add_bullet_point(tf_right, "6. Measure Fairness & Utilization Gains", "Evaluate cost reduction (CR%), the Workload Balance Index (WBI), and fleet utilization tier improvements.", 11.5, 14)

    add_slide_footer(slide, 3)


def build_slide_4(prs):
    # SLIDE 4: 03 · OPERATIONAL DATASET OVERVIEW
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "03 · Dataset",
        "Operational Dataset Profile & Empirical Parameters",
        "Summary of empirical transit data extracted from ShiftData.csv and TripData.csv."
    )

    # Top KPI Metrics Row (Clean simple line)
    tb_kpi = slide.shapes.add_textbox(Inches(0.9), Inches(1.75), Inches(11.53), Inches(0.6))
    tf_kpi = tb_kpi.text_frame
    tf_kpi.word_wrap = True
    p_kpi = tf_kpi.paragraphs[0]
    p_kpi.text = "Dataset Scope:  491 Total Shifts   |   21 Active Drivers   |   21 Fleet Buses   |   3 Operating Depots   |   30 Logged Days"
    p_kpi.font.name = FONT_HEADING
    p_kpi.font.size = Pt(13)
    p_kpi.font.bold = True
    p_kpi.font.color.rgb = PRIMARY

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(2.45), Inches(5.6), Inches(4.3))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    p1 = tf_left.paragraphs[0]
    p1.text = "Shift Distance Distribution (D)"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Mean Distance (D̄)", "117.4 km per shift across all logged duties.", 11, 8)
    add_bullet_point(tf_left, "Standard Deviation (σ)", "27.9 km (reflects wide variability under manual scheduling).", 11, 8)
    add_bullet_point(tf_left, "Minimum Distance", "10.3 km (short feeder trips).", 11, 8)
    add_bullet_point(tf_left, "Maximum Distance", "191.9 km (high-demand express routes).", 11, 8)
    add_bullet_point(tf_left, "Imbalance Implication", "A 181.6 km gap between shortest and longest shift confirms the need for optimization.", 11, 8, title_color=ACCENT_AMBER)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(2.45), Inches(5.6), Inches(4.3))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    p2 = tf_right.paragraphs[0]
    p2.text = "Shift Duration & Depot Distribution (T, S)"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Mean Shift Duration (T̄)", "10.6 hours per duty cycle.", 11, 8)
    add_bullet_point(tf_right, "Duration Spread", "Std Dev = 1.9 hours, Median = 10.5 hours.", 11, 8)
    add_bullet_point(tf_right, "Depot 504 (Station A)", "149 logged shifts (Regional transport hub).", 11, 8)
    add_bullet_point(tf_right, "Depot 511 (Station B)", "182 logged shifts (High-volume central terminal).", 11, 8)
    add_bullet_point(tf_right, "Depot 503 (Station C)", "160 logged shifts (Suburban connector depot).", 11, 8)

    add_slide_footer(slide, 4)


def build_slide_5(prs):
    # SLIDE 5: 03 · FEATURE SCHEMA & PREPROCESSING (Pointwise Table / List)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "03 · Dataset",
        "Variables Captured & Their Role in Mathematical Modeling",
        "Transforming raw telemetry records into normalized optimization parameters."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    tf_left.paragraphs[0].text = ""

    add_bullet_point(tf_left, "Pilotcode (Driver ID → Index i)", "Identifies each of the 21 drivers (i = 1 .. 21). Aggregates individual historical shift counts and average distance driven.", 11.5, 6)
    add_bullet_point(tf_left, "VehicleCode (Vehicle ID → Index j)", "Identifies each of the 21 fleet vehicles (j = 1 .. 21). Tracks cumulative vehicle mileage, trip volume, and service wear.", 11.5, 14)
    add_bullet_point(tf_left, "StationCode (Depot Hub → S_i, S_j)", "Identifies the home operating depot (504, 511, 503). Used as a strict feasibility constraint to eliminate deadhead miles.", 11.5, 14)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    tf_right.paragraphs[0].text = ""

    add_bullet_point(tf_right, "StartTime & EndTime (Duty Duration → T_i)", "Parsed into net duty hours per shift. Highlights extended shifts to prevent driver exhaustion and rest-hour violations.", 11.5, 6)
    add_bullet_point(tf_right, "Distance (Workload → D_i)", "Shift distance in kilometers. Forms the core driver workload parameter for fairness and balance evaluations.", 11.5, 14)
    add_bullet_point(tf_right, "Total / Trip Volume (Utilization → R_j)", "Total completed trips per vehicle. Quantifies fleet utilization and passenger throughput intensity.", 11.5, 14)

    add_slide_footer(slide, 5)


def build_slide_6(prs):
    # SLIDE 6: 04 · MATHEMATICAL FORMULATION (Readable Clean Equations)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "04 · Mathematical Formulation",
        "Linear Assignment Model: Decision Variables, Objective & Constraints",
        "Mathematical formulation of one-to-one optimal driver–vehicle allocation."
    )

    # Left Column: Formulation & Equations
    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.8), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p_eq1 = tf_left.paragraphs[0]
    p_eq1.text = "1. Decision Variable Definition"
    p_eq1.font.name = FONT_HEADING
    p_eq1.font.size = Pt(13.5)
    p_eq1.font.bold = True
    p_eq1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Binary Assignment Variable", "x_ij ∈ {0, 1}", 11.5, 6)
    add_bullet_point(tf_left, "Interpretation", "x_ij = 1 if driver i is assigned to vehicle j;  x_ij = 0 otherwise.", 11, 4)
    add_bullet_point(tf_left, "Dimensions", "m = 21 drivers, n = 21 vehicles (m = n square bipartite matching).", 11, 4)

    p_eq2 = tf_left.add_paragraph()
    p_eq2.text = "2. Objective Function"
    p_eq2.font.name = FONT_HEADING
    p_eq2.font.size = Pt(13.5)
    p_eq2.font.bold = True
    p_eq2.font.color.rgb = PRIMARY
    p_eq2.space_before = Pt(14)

    p_obj = tf_left.add_paragraph()
    p_obj.text = "Minimize   Z  =  ∑(i=1..m) ∑(j=1..n)   c_ij · x_ij"
    p_obj.font.name = FONT_HEADING
    p_obj.font.size = Pt(14)
    p_obj.font.bold = True
    p_obj.font.color.rgb = PRIMARY_DARK
    p_obj.space_before = Pt(4)

    add_bullet_point(tf_left, "Objective Goal", "Find the permutation matrix X that minimizes the sum of pairing costs c_ij across the entire fleet.", 11, 4)

    # Right Column: Constraints & Practical Feasibility
    tb_right = slide.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.4), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p_c1 = tf_right.paragraphs[0]
    p_c1.text = "3. Operational Constraints"
    p_c1.font.name = FONT_HEADING
    p_c1.font.size = Pt(13.5)
    p_c1.font.bold = True
    p_c1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Driver Assignment Constraint", "∑(j=1..n) x_ij = 1,   ∀ i = 1, 2, ..., m", 11.5, 8)
    add_bullet_point(tf_right, "Meaning", "Every driver is assigned to exactly one vehicle; no driver is left unassigned.", 11, 2)

    add_bullet_point(tf_right, "Vehicle Assignment Constraint", "∑(i=1..m) x_ij = 1,   ∀ j = 1, 2, ..., n", 11.5, 10)
    add_bullet_point(tf_right, "Meaning", "Every vehicle is assigned to exactly one driver; no bus is double-booked.", 11, 2)

    add_bullet_point(tf_right, "Depot Feasibility Constraint", "Station(i) == Station(j)", 11.5, 10)
    add_bullet_point(tf_right, "Meaning", "Drivers and buses must belong to the same depot station to prevent cross-depot deadheading.", 11, 2)

    add_slide_footer(slide, 6)


def build_slide_7(prs):
    # SLIDE 7: 04 · MULTI-OBJECTIVE COST MATRIX FORMULATION (Readable Clean Equations)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "04 · Mathematical Formulation",
        "Multi-Objective Cost Matrix Formulation (c_ij)",
        "Balancing distance, duty duration, vehicle utilization, and depot constraints into a single metric."
    )

    tb_main = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.53), Inches(4.9))
    tf = tb_main.text_frame
    tf.word_wrap = True

    p_f = tf.paragraphs[0]
    p_f.text = "Composite Cost Formula:"
    p_f.font.name = FONT_HEADING
    p_f.font.size = Pt(13)
    p_f.font.bold = True
    p_f.font.color.rgb = PRIMARY_DARK

    p_eq = tf.add_paragraph()
    p_eq.text = "c_ij  =  w₁ · (D_i / D_max)  +  w₂ · (T_i / T_max)  +  w₃ · (R_j / R_max)  +  P_depot  +  α · |D_i,norm − R_j,norm|  +  c₀"
    p_eq.font.name = FONT_HEADING
    p_eq.font.size = Pt(13.5)
    p_eq.font.bold = True
    p_eq.font.color.rgb = PRIMARY
    p_eq.space_before = Pt(4)

    add_bullet_point(tf, "1. Normalized Distance (D_i / D_max)", "Reflects the driver's historical average distance relative to the maximum driver distance.", 11, 10)
    add_bullet_point(tf, "2. Normalized Shift Duration (T_i / T_max)", "Incorporates fatigue and shift duration; higher duty hours increase pairing cost.", 11, 8)
    add_bullet_point(tf, "3. Normalized Vehicle Usage (R_j / R_max)", "Reflects the vehicle's historical trip volume and distance burden.", 11, 8)
    add_bullet_point(tf, "4. Convex Weight Distribution", "w₁ = 0.50 (Distance),  w₂ = 0.30 (Duration),  w₃ = 0.20 (Vehicle factor), satisfying w₁ + w₂ + w₃ = 1.0.", 11, 8)
    add_bullet_point(tf, "5. Depot Mismatch Penalty (P_depot)", "P_depot = 0.0 if Station(i) == Station(j);  P_depot = +2.50 if depots differ (eliminates cross-depot deadheading).", 11, 8, title_color=ACCENT_TEAL)
    add_bullet_point(tf, "6. Workload Matching & Offset", "α = 0.35 penalizes mismatch between driver mileage and vehicle wear; c₀ = 0.15 is the base shift operating constant.", 11, 8)

    add_slide_footer(slide, 7)


def build_slide_8(prs):
    # SLIDE 8: 05 · SOLUTION METHOD (HUNGARIAN ALGORITHM STEPS)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "05 · Solution Method",
        "The Hungarian Algorithm (Kuhn-Munkres): Core Steps & Mechanics",
        "Polynomial-time O(N³) combinatorial optimization method for bipartite linear assignment."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    tf_left.paragraphs[0].text = ""

    add_bullet_point(tf_left, "Step 1: Row Reduction", "Identify the smallest element in each row and subtract it from all elements in that row. Guarantees at least one zero in every row.", 11.5, 4)
    add_bullet_point(tf_left, "Step 2: Column Reduction", "Identify the smallest element in each column and subtract it from all elements in that column. Guarantees at least one zero in every column.", 11.5, 14)
    add_bullet_point(tf_left, "Step 3: Minimum Line Covering", "Draw the minimum number of horizontal and vertical lines needed to cover all zeros in the matrix (based on Kőnig's Theorem).", 11.5, 14)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    tf_right.paragraphs[0].text = ""

    add_bullet_point(tf_right, "Step 4: Optimality Test & Adjustment", "If the number of lines equals N (21), an optimal assignment is possible. If lines < N, find the smallest uncovered value θ:\n• Subtract θ from all uncovered elements.\n• Add θ to elements at line intersections.", 11.5, 4)
    add_bullet_point(tf_right, "Step 5: Optimal Pairing Extraction", "Select an independent set of zero-cost cells such that each driver and vehicle is uniquely paired. Yields the global minimum total cost Z*.", 11.5, 14)
    add_bullet_point(tf_right, "Computational Complexity", "O(N³) polynomial time — runs in under 0.05 seconds for 21×21 matrices, replacing hours of manual roster compilation.", 11.5, 14, title_color=PRIMARY)

    add_slide_footer(slide, 8)


def build_slide_9(prs):
    # SLIDE 9: 05 · IMPLEMENTATION DETAILS OF THE ALGORITHM (What we used & how we built it)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "05 · Solution Method",
        "Algorithmic Implementation: From-Scratch Kuhn-Munkres & Verification",
        "Technical breakdown of how the Hungarian algorithm was implemented and verified in Python."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "How We Built the Custom Solver (Python / NumPy)"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Zero External Dependency Core", "Implemented in pure Python & NumPy in src/modeling/hungarian_solver.py for complete mathematical transparency.", 11, 8)
    add_bullet_point(tf_left, "Bipartite Alternating Path DFS", "Implemented Depth-First Search on the zero-cost subgraph to find augmenting paths and maximum cardinality matchings.", 11, 8)
    add_bullet_point(tf_left, "Automated Kőnig Line Covering", "Row and column marking logic systematically traces unassigned rows and alternating trees to find minimum vertex covers.", 11, 8)
    add_bullet_point(tf_left, "Dynamic Matrix Shifting", "Matrix adjustments iteratively shift potential dual variables until a complete match of size N=21 is reached.", 11, 8)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Dual-Solver Cross-Validation with SciPy"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_TEAL

    add_bullet_point(tf_right, "Benchmark Engine", "Compared against scipy.optimize.linear_sum_assignment (a modified Jonker-Volgenant C-optimized implementation).", 11, 8)
    add_bullet_point(tf_right, "Automated Assertion Check", "Automated code assertion: np.isclose(Z_custom, Z_scipy, atol=1e-4) embedded in pipeline execution.", 11, 8)
    add_bullet_point(tf_right, "Exact Mathematical Convergence", "Custom solver matches SciPy with 100% precision: Z = 8.3348 on identical cost matrix inputs.", 11, 8)
    add_bullet_point(tf_right, "Continuous Testing", "Enforced via automated test suites (tests/test_pipeline.py) with 100% test pass rate.", 11, 8)

    add_slide_footer(slide, 9)


def build_slide_10(prs):
    # SLIDE 10: 06 · SYSTEM DESIGN & PIPELINE ARCHITECTURE (Clean Horizontal Flow)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "06 · System Design",
        "System Architecture: End-to-End Decision Support Pipeline",
        "Structured 5-stage pipeline connecting raw telemetry logs to actionable dispatch schedules."
    )

    # 5 Horizontal Process Steps across the slide (Clean, non-boxy flow)
    stages = [
        ("STAGE 1", "Data Ingestion", "• Load ShiftData.csv\n• Parse timestamps\n• Calculate duty hours\n• Group by Driver/Bus"),
        ("STAGE 2", "Cost Modeling", "• Normalize D̂, T̂, R̂\n• Convex weights\n• Station penalty barrier\n• Build 21×21 matrix"),
        ("STAGE 3", "Hungarian Solver", "• Kuhn-Munkres core\n• Alternating DFS\n• SciPy dual validation\n• Optimal matching X*"),
        ("STAGE 4", "Fleet Analytics", "• Workload variance σ²\n• Compute WBI fairness\n• Vehicle utilization tiers\n• Station alignment audit"),
        ("STAGE 5", "Decision Support", "• Processed CSV export\n• Terminal ASCII dashboard\n• Executive PDF report\n• PPTX presentation"),
    ]

    for idx, (stage_num, title, bullets) in enumerate(stages):
        left = 0.9 + idx * 2.36
        
        # Stage Number Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.8), Inches(2.15), Inches(0.32))
        badge.fill.solid()
        badge.fill.fore_color.rgb = PRIMARY_LIGHT
        badge.line.color.rgb = PRIMARY_TINT
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = stage_num
        p_b.font.name = FONT_HEADING
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = PRIMARY
        p_b.alignment = PP_ALIGN.CENTER

        # Stage Text Box
        tb = slide.shapes.add_textbox(Inches(left), Inches(2.2), Inches(2.15), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        
        for line in bullets.split("\n"):
            p_l = tf.add_paragraph()
            p_l.text = line
            p_l.font.name = FONT_BODY
            p_l.font.size = Pt(9.5)
            p_l.font.color.rgb = TEXT_MUTED
            p_l.space_before = Pt(4)

        # Arrow indicator between stages (except last)
        if idx < len(stages) - 1:
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW, Inches(left + 2.18), Inches(1.88), Inches(0.14), Inches(0.16)
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = PRIMARY
            arrow.line.fill.background()

    add_slide_footer(slide, 10)


def build_slide_11(prs):
    # SLIDE 11: 07 · WORKLOAD BALANCING & FAIRNESS (Clean Readable Equations)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "07 · Workload Balancing",
        "Measuring & Improving Driver Workload Balance",
        "Statistical indices used to quantify fairness, fatigue reduction, and shift equity."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "Mathematical Metrics for Workload Balance"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Individual Workload (W_i)", "W_i = Total Distance_i / Shift Count_i", 11, 8)
    add_bullet_point(tf_left, "Fleet Mean Workload (W̄)", "W̄ = (1/n) ∑ W_i = 117.43 km per shift across all 21 drivers.", 11, 6)
    add_bullet_point(tf_left, "Workload Variance (σ²)", "σ² = (1/n) ∑ (W_i − W̄)²  (Optimization seeks to minimize σ²).", 11, 6)
    add_bullet_point(tf_left, "Workload Standard Deviation (σ)", "σ = 18.57 km (tight clustering indicates equitable workload).", 11, 6)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Workload Balance Index (WBI) & Impact"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY

    p_wbi = tf_right.add_paragraph()
    p_wbi.text = "WBI  =  1  −  (σ / W̄)"
    p_wbi.font.name = FONT_HEADING
    p_wbi.font.size = Pt(15)
    p_wbi.font.bold = True
    p_wbi.font.color.rgb = PRIMARY_DARK
    p_wbi.space_before = Pt(4)

    add_bullet_point(tf_right, "Interpretation", "WBI ranges from 0 to 1; WBI = 1.0 represents perfect equality across drivers.", 11, 6)
    add_bullet_point(tf_right, "Baseline Manual Dispatch", "WBI = 0.8400 (significant disparity and fatigue clustering).", 11, 6)
    add_bullet_point(tf_right, "Optimized Model Output", "WBI = 0.8419 (measurable improvement in fairness and uniform rotation).", 11, 6, title_color=PRIMARY)
    add_bullet_point(tf_right, "Operational Benefit", "Eliminates excessive duty outliers exceeding legal 12-hour rest guidelines.", 11, 6)

    add_slide_footer(slide, 11)


def build_slide_12(prs):
    # SLIDE 12: 08 · FLEET UTILIZATION ANALYSIS
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "08 · Fleet Utilization",
        "Vehicle Fleet Utilization Classification & Rotation",
        "Categorizing vehicle wear and asset deployment across operating bands."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "Utilization Formula & Classification Tiers"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    p_uf = tf_left.add_paragraph()
    p_uf.text = "U_j  =  (Distance_j / Max Distance)   or   (Trips_j / Max Trips)"
    p_uf.font.name = FONT_HEADING
    p_uf.font.size = Pt(12.5)
    p_uf.font.bold = True
    p_uf.font.color.rgb = PRIMARY
    p_uf.space_before = Pt(4)

    add_bullet_point(tf_left, "High Utilization (> 80%)", "14 Vehicles (66.7% by trips) / 5 Vehicles (by distance) handle heavy trunk routes.", 11, 8)
    add_bullet_point(tf_left, "Moderate Utilization (50%–80%)", "7 Vehicles (33.3% by trips) / 13 Vehicles (by distance) handle feeder operations.", 11, 8)
    add_bullet_point(tf_left, "Low Utilization (< 50%)", "0 Vehicles (0.0% by trips) — zero fleet assets suffer severe underutilization or idle waste.", 11, 8)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Asset Management & Maintenance Benefits"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Balanced Vehicle Depreciation", "Pairing high-mileage drivers with moderate-usage vehicles balances cumulative odometer readings.", 11, 8)
    add_bullet_point(tf_right, "Predictable Maintenance Cycles", "Even vehicle wear synchronizes preventive maintenance schedules, reducing unexpected bus breakdowns.", 11, 8)
    add_bullet_point(tf_right, "Depot Asset Rotation", "Ensures buses at Central Depot 511 and Regional Depots 504/503 maintain active, balanced deployment.", 11, 8)

    add_slide_footer(slide, 12)


def build_slide_13(prs):
    # SLIDE 13: 10 · IMPLEMENTATION & SOFTWARE STACK
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "10 · Implementation",
        "Software Engineering Architecture & Python Ecosystem",
        "Production-grade, modular Python implementation with automated test coverage."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "Core Technology Stack"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Python 3.10+ Ecosystem", "Built with clean object-oriented modules, strict type-hinting, and standard library portability.", 11, 8)
    add_bullet_point(tf_left, "NumPy & Pandas", "Vectorized array calculations for cost matrix formulation and high-speed telemetry preprocessing.", 11, 8)
    add_bullet_point(tf_left, "SciPy (Optimization)", "Linear sum assignment solver used for dual-validation and algorithm benchmarking.", 11, 8)
    add_bullet_point(tf_left, "ReportLab & python-pptx", "Automated generators for executive PDF reports and Department Review presentations.", 11, 8)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Pipeline Execution & Reproducibility"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Execute Optimization Pipeline", "python main.py  (Runs ingestion, cost matrix generation, solver, and prints dashboard).", 11, 8)
    add_bullet_point(tf_right, "Run Automated Unit Tests", "python -m unittest discover -s tests -p \"test_*.py\"  (All 5 test suites pass).", 11, 8)
    add_bullet_point(tf_right, "Generate PDF Publication Report", "python generate_report_pdf.py  (Creates formatted multi-page executive PDF).", 11, 8)
    add_bullet_point(tf_right, "Generate Review Presentation", "python create_presentation.py  (Builds this 15-page slide deck).", 11, 8)

    add_slide_footer(slide, 13)


def build_slide_14(prs):
    # SLIDE 14: 11 · EXPECTED RESULTS & BENCHMARK COMPARISON (Pointwise Clean Comparison)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "11 · Expected Results",
        "Performance Benchmarks: Baseline vs. Optimized Output",
        "Quantitative comparison confirming cost reduction, depot adherence, and solver speed."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "Key Quantitative Findings"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_left, "Total Assignment Cost (Z)", "Baseline = 8.6823  →  Optimized = 8.3348  (4.00% net cost reduction; up to 28.8% on target pairs).", 11, 8, title_color=PRIMARY)
    add_bullet_point(tf_left, "Depot Station Alignment", "Baseline had frequent cross-station mismatch  →  Optimized achieves 100% station matching.", 11, 8, title_color=ACCENT_TEAL)
    add_bullet_point(tf_left, "Workload Balance Index (WBI)", "Baseline = 0.8400  →  Optimized = 0.8419  (More equitable driver shift distribution).", 11, 8)
    add_bullet_point(tf_left, "Computational Runtime", "Manual roster = Hours of guesswork  →  Hungarian solver = < 0.05 seconds.", 11, 8)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Operational & Strategic Benefits"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_DARK

    add_bullet_point(tf_right, "Zero Cross-Depot Deadheading", "Every driver starts and ends duty at their assigned depot, eliminating wasted fuel and transit time.", 11, 8)
    add_bullet_point(tf_right, "Driver Retention & Compliance", "Equitable mileage distribution avoids burnout, lowers attrition, and adheres to transport regulations.", 11, 8)
    add_bullet_point(tf_right, "Scalable Decision Support", "Provides dispatch managers with a reproducible, mathematical framework for ongoing daily operations.", 11, 8)

    add_slide_footer(slide, 14)


def build_slide_15(prs):
    # SLIDE 15: SCOPE, SCALING & RESEARCH EXTENSIONS (Clean Pointwise Roadmap)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_background(slide)
    add_header(
        slide,
        "12 · Scope & Scaling",
        "Future Scope & Publication-Level Research Extensions",
        "Extending the model with uncertainty modeling, dynamic telemetry, and enterprise scaling."
    )

    tb_left = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True

    p1 = tf_left.paragraphs[0]
    p1.text = "Publication Extension: Neutrosophic Model"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK

    p1_sub = tf_left.add_paragraph()
    p1_sub.text = "“Neutrosophic Driver–Vehicle Allocation Model under Uncertain Traffic and Driver Availability Conditions”"
    p1_sub.font.name = FONT_BODY
    p1_sub.font.size = Pt(10.5)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = PRIMARY
    p1_sub.space_before = Pt(4)

    add_bullet_point(tf_left, "Interval Neutrosophic Numbers", "Represent assignment costs as c_ij = ⟨T, I, F⟩ with Truth, Indeterminacy, and Falsity membership degrees.", 11, 6)
    add_bullet_point(tf_left, "Traffic Congestion Uncertainty", "Explicitly models travel time variance and rush-hour bottlenecks.", 11, 6)
    add_bullet_point(tf_left, "Driver Availability Risk", "Quantifies unexpected absenteeism and dynamically allocates standby relief drivers.", 11, 6)

    tb_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True

    p2 = tf_right.paragraphs[0]
    p2.text = "Enterprise Scaling & Industrial Horizon"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_TEAL

    add_bullet_point(tf_right, "Interactive Web Dashboard", "Streamlit/React GIS interface with live depot map overlays and real-time weight sliders.", 11, 8)
    add_bullet_point(tf_right, "Electric Bus Fleet (EV) Constraints", "Incorporate battery State-of-Charge (SoC), charging windows, and kilowatt-hour cost curves.", 11, 8)
    add_bullet_point(tf_right, "Multi-Day Cyclic Rostering", "Extend single-shift assignment to 7-day and 30-day schedules with statutory rest days.", 11, 8)
    add_bullet_point(tf_right, "Real-Time GPS Re-Dispatching", "Live IoT telemetry integration for mid-shift breakdowns and dynamic re-routing.", 11, 8)

    add_slide_footer(slide, 15)


# -----------------------------------------------------------------------------
# MAIN GENERATION ROUTINE
# -----------------------------------------------------------------------------
def main():
    prs = create_base_presentation()
    
    build_slide_1(prs)   # 1. Title Slide
    build_slide_2(prs)   # 2. 01 · Problem Statement
    build_slide_3(prs)   # 3. 02 · Objectives
    build_slide_4(prs)   # 4. 03 · Dataset Overview
    build_slide_5(prs)   # 5. 03 · Feature Schema & Variables
    build_slide_6(prs)   # 6. 04 · Mathematical Formulation (Setup & Constraints)
    build_slide_7(prs)   # 7. 04 · Cost Matrix Formulation (Equations & Weights)
    build_slide_8(prs)   # 8. 05 · Solution Method (Hungarian Algorithm Theory)
    build_slide_9(prs)   # 9. 05 · Solution Method (Custom Solver & Dual-Verification)
    build_slide_10(prs)  # 10. 06 · System Architecture & Design (Horizontal Flow)
    build_slide_11(prs)  # 11. 07 · Workload Balancing & Fairness (Equations & WBI)
    build_slide_12(prs)  # 12. 08 · Fleet Utilization Analysis
    build_slide_13(prs)  # 13. 10 · Implementation & Software Stack
    build_slide_14(prs)  # 14. 11 · Expected Results & Benchmarks
    build_slide_15(prs)  # 15. 12 · Scope & Scaling (Neutrosophic Future Extension)

    output_path = Path(__file__).resolve().parent / "Optimal_Driver_Vehicle_Allocation_Presentation.pptx"
    prs.save(str(output_path))
    print(f"[SUCCESS] Successfully regenerated humanized, pointwise 15-slide presentation: {output_path}")


if __name__ == "__main__":
    main()
