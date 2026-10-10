"""
========================================================================================
Concrete Compressive Strength Predictor & Mix Quality Assessment System
========================================================================================
A modern, engineering-grade Gradio application for assessing concrete mix designs 
and predicting compressive strength (MPa) using the pre-trained ML bundle:
'concrete_model.pkl'.

Usage:
    python app.py
========================================================================================
"""

import os
import joblib
import pandas as pd
import numpy as np
import gradio as gr

# ---------------------------------------------------------------------------
# 1. Model Loading (Executed Once at Startup)
# ---------------------------------------------------------------------------
MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "concrete_model.pkl")

if not os.path.exists(MODEL_FILE):
    MODEL_FILE = "concrete_model.pkl"

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(f"Model bundle 'concrete_model.pkl' not found at {MODEL_FILE}")

bundle = joblib.load(MODEL_FILE)

regressor = bundle["regressor"]
classifier = bundle["classifier"]
cutoff = float(bundle["cutoff"])

print("=" * 65)
print(" Concrete Compressive Strength Model Loaded Successfully")
print(f"  - Regressor Pipeline: {type(regressor).__name__}")
print(f"  - Classifier Object : {'Dedicated Classifier' if classifier is not None else 'None (Cutoff Comparison Mode)'}")
print(f"  - Quality Benchmark : Cutoff = {cutoff:.2f} MPa")
print("=" * 65)


# ---------------------------------------------------------------------------
# 2. Feature Engineering Function
# ---------------------------------------------------------------------------
def add_features(data):
    """Takes a DataFrame with the 8 original input columns and adds new features."""
    data = data.copy()

    # Water compared to cement
    data["Water_Cement_Ratio"] = data["Water"] / data["Cement"]

    # Total binder = cement + slag + fly ash
    data["Binder"] = data["Cement"] + data["Blast_Furnace_Slag"] + data["Fly_Ash"]

    # Water compared to total binder
    data["Water_Binder_Ratio"] = data["Water"] / data["Binder"]

    # Strength grows fast at early ages, then slows down -> use log of age
    data["Log_Age"] = np.log1p(data["Age"])

    return data


# ---------------------------------------------------------------------------
# 3. UI Display Formatters & Component Generators
# ---------------------------------------------------------------------------
def format_initial_card(cutoff_val):
    """Renders the initial standby card before calculation."""
    return f"""
    <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 26px 22px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow: 0 4px 14px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">
                Assessment Status
            </span>
            <span style="display: inline-flex; align-items: center; gap: 6px; background: #f1f5f9; color: #475569; padding: 5px 14px; border-radius: 9999px; font-weight: 600; font-size: 12px; border: 1px solid #cbd5e1;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background: #94a3b8; display: inline-block;"></span>
                Ready for Evaluation
            </span>
        </div>

        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px; padding: 36px 20px; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 15px; font-weight: 700; color: #334155; margin-bottom: 6px;">
                Awaiting Mix Design Evaluation
            </div>
            <div style="font-size: 13px; color: #64748b; max-width: 340px; margin: 0 auto; line-height: 1.5;">
                Configure the mixture sliders on the left or click any preset in the <b>Mix Examples</b> below, then click <b>Predict Strength</b>.
            </div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; font-size: 12px; color: #475569; line-height: 1.6;">
            <div style="font-weight: 700; color: #1e293b; margin-bottom: 3px;">
                Classification Benchmark:
            </div>
            A mix is categorized as <b>STRONG</b> if predicted compressive strength meets or exceeds the training dataset median (<b>{cutoff_val:.2f} MPa</b>). Mixes below this threshold are categorized as <b>WEAK</b>.
        </div>
    </div>
    """


def format_result_card(strength, is_strong, cutoff_val, wc_ratio, wb_ratio, total_binder, age):
    """Renders a clean, modern card highlighting strength, status, and engineering indices."""
    status_label = "STRONG" if is_strong else "WEAK"

    if is_strong:
        card_bg = "#f0fdf4"             # Soft calm green background
        card_border = "#86efac"         # Subtle emerald border
        badge_bg = "#dcfce7"
        badge_text = "#15803d"
        dot_color = "#16a34a"
        bar_fill_color = "#22c55e"
        status_sub = f"Exceeds structural cutoff benchmark (≥ {cutoff_val:.2f} MPa)"
        tag_desc = "Structural Grade Mix"
    else:
        card_bg = "#fff7ed"             # Soft warm amber background
        card_border = "#fdba74"         # Subtle amber border
        badge_bg = "#ffedd5"
        badge_text = "#c2410c"
        dot_color = "#ea580c"
        bar_fill_color = "#f97316"
        status_sub = f"Below structural cutoff benchmark (< {cutoff_val:.2f} MPa)"
        tag_desc = "Moderate / Non-Structural Mix"

    # Relative scale for strength visualizer (0 to 85 MPa reference span)
    bar_width = min(max((strength / 85.0) * 100, 3.0), 100.0)
    cutoff_mark = min(max((cutoff_val / 85.0) * 100, 0.0), 100.0)
    strength_psi = strength * 145.038

    return f"""
    <div style="background: {card_bg}; border: 1.5px solid {card_border}; border-radius: 16px; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow: 0 4px 16px rgba(0,0,0,0.04); transition: all 0.3s ease;">
        
        <!-- Status Header Row -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">
                    Assessment Result
                </span>
                <div style="font-size: 13px; font-weight: 500; color: #475569; margin-top: 1px;">
                    {status_sub}
                </div>
            </div>
            <div style="display: inline-flex; align-items: center; gap: 7px; background: {badge_bg}; color: {badge_text}; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 13px; letter-spacing: 0.05em; border: 1px solid {card_border};">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {dot_color}; display: inline-block;"></span>
                {status_label} MIX
            </div>
        </div>

        <!-- Primary Output Callout -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 20px; text-align: center; margin-bottom: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #64748b; margin-bottom: 6px;">
                Predicted Compressive Strength
            </div>
            <div style="font-size: 46px; font-weight: 800; color: #0f172a; line-height: 1.1; letter-spacing: -0.02em;">
                {strength:.2f} <span style="font-size: 20px; font-weight: 600; color: #64748b;">MPa</span>
            </div>
            <div style="font-size: 13px; color: #64748b; margin-top: 6px; font-weight: 500;">
                {strength_psi:,.0f} psi &bull; <span style="color: {badge_text}; font-weight: 600;">{tag_desc}</span>
            </div>

            <!-- Strength vs Cutoff Visualizer -->
            <div style="margin-top: 20px; text-align: left;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; margin-bottom: 5px; font-weight: 600;">
                    <span>0 MPa</span>
                    <span style="color: #b91c1c;">Cutoff: {cutoff_val:.2f} MPa</span>
                    <span>85 MPa</span>
                </div>
                <div style="position: relative; height: 10px; background: #f1f5f9; border-radius: 6px; overflow: visible; border: 1px solid #e2e8f0;">
                    <div style="position: absolute; left: 0; top: 0; bottom: 0; width: {bar_width:.1f}%; background: {bar_fill_color}; border-radius: 5px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                    <div style="position: absolute; left: {cutoff_mark:.1f}%; top: -4px; bottom: -4px; width: 2.5px; background: #dc2626; border-radius: 2px; z-index: 2;" title="Median Cutoff ({cutoff_val:.2f} MPa)"></div>
                </div>
            </div>
        </div>

        <!-- Calculated Mix Properties Grid -->
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 18px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Water / Cement (w/c)</div>
                <div style="font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 3px;">{wc_ratio:.2f}</div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Water / Binder (w/b)</div>
                <div style="font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 3px;">{wb_ratio:.2f}</div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Total Binder Content</div>
                <div style="font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 3px;">{total_binder:.1f} <span style="font-size: 11px; font-weight: 500; color: #64748b;">kg/m³</span></div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em;">Curing Period</div>
                <div style="font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 3px;">{age:.0f} <span style="font-size: 11px; font-weight: 500; color: #64748b;">Days</span></div>
            </div>
        </div>

        <!-- Explanatory Context Footer -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; font-size: 12px; color: #64748b; line-height: 1.5;">
            <div style="font-weight: 700; color: #334155; margin-bottom: 2px;">Evaluation Benchmark:</div>
            The <b>{status_label}</b> designation is determined by comparing the predicted compressive strength ({strength:.2f} MPa) against the training set median cutoff threshold (<b>{cutoff_val:.2f} MPa</b>).
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# 4. Prediction Pipeline & Event Handlers
# ---------------------------------------------------------------------------
def predict_mix_ui(cement, slag, fly_ash, water, superplasticizer, coarse_agg, fine_agg, age):
    """Processes mix ingredients, generates model prediction, and returns formatted result card."""
    raw_dict = {
        "Cement": float(cement),
        "Blast_Furnace_Slag": float(slag),
        "Fly_Ash": float(fly_ash),
        "Water": float(water),
        "Superplasticizer": float(superplasticizer),
        "Coarse_Aggregate": float(coarse_agg),
        "Fine_Aggregate": float(fine_agg),
        "Age": float(age)
    }

    # Prepare DataFrame and calculate the 4 engineered features
    df_raw = pd.DataFrame([raw_dict])
    df_featured = add_features(df_raw)

    # Compressive strength prediction (Regression)
    strength = float(regressor.predict(df_featured)[0])

    # Quality classification (Strong or Weak)
    if classifier is None:
        is_strong = strength >= cutoff
    else:
        is_strong = bool(classifier.predict(df_featured)[0] == 1)

    # Civil engineering metrics
    wc_ratio = df_featured["Water_Cement_Ratio"].iloc[0]
    wb_ratio = df_featured["Water_Binder_Ratio"].iloc[0]
    total_binder = df_featured["Binder"].iloc[0]

    return format_result_card(strength, is_strong, cutoff, wc_ratio, wb_ratio, total_binder, age)


def reset_to_defaults():
    """Resets all 8 input sliders to standard defaults and restores initial assessment card."""
    return (
        280.0,  # Cement
        0.0,    # Slag
        0.0,    # Fly Ash
        180.0,  # Water
        0.0,    # Superplasticizer
        970.0,  # Coarse Aggregate
        780.0,  # Fine Aggregate
        28.0,   # Age
        format_initial_card(cutoff)
    )


# ---------------------------------------------------------------------------
# 5. Gradio Interface Layout & Modern CSS Theme
# ---------------------------------------------------------------------------
custom_css = """
.gradio-container {
    max-width: 1220px !important;
    margin: 0 auto !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

.header-banner {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: #ffffff;
    margin-bottom: 22px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.08);
}

.group-container {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}

.btn-predict {
    background: #0f172a !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12) !important;
    transition: transform 0.15s ease, background 0.15s ease !important;
}
.btn-predict:hover {
    background: #1e293b !important;
    transform: translateY(-1px);
}

.btn-reset {
    background: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 10px !important;
    padding: 12px 18px !important;
}
.btn-reset:hover {
    background: #f1f5f9 !important;
    color: #1e293b !important;
}
"""

with gr.Blocks(title="Concrete Compressive Strength Predictor") as demo:

    # Header Section
    gr.HTML(f"""
    <div class="header-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin-bottom: 4px;">
                    Civil & Materials Engineering ML Assessment
                </div>
                <h1 style="font-size: 26px; font-weight: 800; margin: 0; color: #ffffff; letter-spacing: -0.02em;">
                    Concrete Compressive Strength Predictor
                </h1>
                <div style="font-size: 14px; color: #cbd5e1; margin-top: 6px; max-width: 650px; line-height: 1.4;">
                    Dual-task machine learning interface providing compressive strength estimation (MPa) and structural quality classification.
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 10px; padding: 8px 14px; font-size: 12px; color: #e2e8f0; text-align: right;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Benchmark Cutoff</div>
                    <div style="font-weight: 700; color: #ffffff;">{cutoff:.2f} MPa</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 10px; padding: 8px 14px; font-size: 12px; color: #e2e8f0; text-align: right;">
                    <div style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Model Engine</div>
                    <div style="font-weight: 700; color: #ffffff;">Gradient Boosting</div>
                </div>
            </div>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        # Left Column: Structured Mix Inputs (Grouped into 4 Logical Categories)
        with gr.Column(scale=3):

            # Group 1: Binder Materials
            with gr.Group(elem_classes=["group-container"]):
                gr.Markdown("#### 1. Binder Materials (Cementitious)")
                cement = gr.Slider(
                    minimum=100.0, maximum=540.0, value=280.0, step=1.0,
                    label="Cement (kg/m³)",
                    info="Standard Portland cement content"
                )
                slag = gr.Slider(
                    minimum=0.0, maximum=360.0, value=0.0, step=1.0,
                    label="Blast Furnace Slag (kg/m³)",
                    info="Granulated blast-furnace slag (SCM)"
                )
                fly_ash = gr.Slider(
                    minimum=0.0, maximum=200.0, value=0.0, step=1.0,
                    label="Fly Ash (kg/m³)",
                    info="Pozzolanic coal combustion fly ash"
                )

            # Group 2: Water & Additives
            with gr.Group(elem_classes=["group-container"]):
                gr.Markdown("#### 2. Water & Chemical Additives")
                water = gr.Slider(
                    minimum=120.0, maximum=250.0, value=180.0, step=1.0,
                    label="Water (kg/m³)",
                    info="Total batch water content"
                )
                superplasticizer = gr.Slider(
                    minimum=0.0, maximum=33.0, value=0.0, step=0.1,
                    label="Superplasticizer (kg/m³)",
                    info="High-range water-reducing admixture"
                )

            # Group 3: Aggregates
            with gr.Group(elem_classes=["group-container"]):
                gr.Markdown("#### 3. Aggregates (Granular Skeleton)")
                coarse_agg = gr.Slider(
                    minimum=800.0, maximum=1150.0, value=970.0, step=1.0,
                    label="Coarse Aggregate (kg/m³)",
                    info="Gravel and crushed stone skeleton"
                )
                fine_agg = gr.Slider(
                    minimum=590.0, maximum=995.0, value=780.0, step=1.0,
                    label="Fine Aggregate (kg/m³)",
                    info="Natural sand or crushed fine sand"
                )

            # Group 4: Curing Conditions
            with gr.Group(elem_classes=["group-container"]):
                gr.Markdown("#### 4. Curing Conditions")
                age = gr.Slider(
                    minimum=1.0, maximum=365.0, value=28.0, step=1.0,
                    label="Curing Age (Days)",
                    info="Moist curing duration prior to compression testing"
                )

            # Action Control Buttons
            with gr.Row():
                predict_btn = gr.Button("Predict Strength", variant="primary", scale=2, elem_classes=["btn-predict"])
                reset_btn = gr.Button("Reset", variant="secondary", scale=1, elem_classes=["btn-reset"])

        # Right Column: Result Card Output
        with gr.Column(scale=2):
            output_card = gr.HTML(value=format_initial_card(cutoff))

    # Pre-configured Examples Section
    gr.Markdown("### Pre-Configured Mix Examples")
    gr.Markdown("Click any mixture design below to automatically load its proportions into the sliders and view the evaluation:")

    example_mixes = [
        [280.0, 100.0, 0.0, 180.0, 5.0, 970.0, 770.0, 28.0],
        [380.0, 95.0, 0.0, 165.0, 8.5, 960.0, 810.0, 28.0],
        [250.0, 0.0, 125.0, 175.0, 5.0, 990.0, 760.0, 56.0],
        [160.0, 0.0, 0.0, 205.0, 0.0, 1050.0, 850.0, 7.0]
    ]

    example_labels = [
        "Standard 28-Day Structural Mix",
        "High-Performance Concrete (HPC)",
        "Fly-Ash Pozzolanic Concrete (56-Day)",
        "Lean / Low-Binder Mix (Weak)"
    ]

    gr.Examples(
        examples=example_mixes,
        inputs=[cement, slag, fly_ash, water, superplasticizer, coarse_agg, fine_agg, age],
        outputs=output_card,
        fn=predict_mix_ui,
        example_labels=example_labels,
        cache_examples=False
    )

    # Event Wiring
    predict_btn.click(
        fn=predict_mix_ui,
        inputs=[cement, slag, fly_ash, water, superplasticizer, coarse_agg, fine_agg, age],
        outputs=[output_card]
    )

    reset_btn.click(
        fn=reset_to_defaults,
        inputs=[],
        outputs=[cement, slag, fly_ash, water, superplasticizer, coarse_agg, fine_agg, age, output_card]
    )

# ---------------------------------------------------------------------------
# 6. Launch Web Interface
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=custom_css, inbrowser=True)
