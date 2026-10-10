# Concrete Compressive Strength Predictor & Mix Quality Assessment

A modern, interactive machine learning web application built with **Gradio 6** for civil engineers, materials scientists, and concrete technologists to predict concrete compressive strength ($f'_c$ in MPa) and classify mix quality into **STRONG** or **WEAK**.

---

## Project Structure

```
final project/
├── UI.ipynb                                # Main Jupyter Notebook with interactive Gradio interface
├── app.py                                  # Standalone Python web application script
├── concrete_model.pkl                      # Trained ML model bundle (Regressor, Cutoff, Classifier)
├── Concrete_Data.xlsx                      # Original Concrete Compressive Strength dataset
├── Concrete_Strength_Analysis_Organized.ipynb # Training, EDA, and model evaluation notebook
├── requirements.txt                        # Required Python packages
└── README.md                               # Project documentation and user guide
```

---

## Quick Start Guide

### Option 1: Run via Jupyter Notebook (`UI.ipynb`)
1. Open [`UI.ipynb`](UI.ipynb) in **VS Code** or **Jupyter Lab**.
2. Select your Python kernel.
3. Click **Run All** cells.
4. The Gradio interface will launch directly inside the notebook or at `http://127.0.0.1:7860`.

### Option 2: Run via Terminal (`app.py`)
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:7860` in your web browser.

---

## Machine Learning Architecture

- **Primary Model Engine:** `GradientBoostingRegressor` pipeline trained on 1,030 mix formulations.
- **Decision Benchmark (Cutoff):** **`33.72 MPa`** (median strength of training distribution).
  - Mixes with compressive strength $\ge 33.72\text{ MPa}$ are classified as **STRONG**.
  - Mixes with compressive strength $< 33.72\text{ MPa}$ are classified as **WEAK**.
- **Engineered Features (`add_features`):**
  - $\text{Water\_Cement\_Ratio} = \text{Water} / \text{Cement}$
  - $\text{Binder} = \text{Cement} + \text{Blast\_Furnace\_Slag} + \text{Fly\_Ash}$
  - $\text{Water\_Binder\_Ratio} = \text{Water} / \text{Binder}$
  - $\text{Log\_Age} = \ln(1 + \text{Age})$

---

## Mixture Input Groups

1. **Binder Materials (kg/m³):**
   - Cement ($100 - 540$)
   - Blast Furnace Slag ($0 - 360$)
   - Fly Ash ($0 - 200$)
2. **Water & Additives (kg/m³):**
   - Water ($120 - 250$)
   - Superplasticizer ($0 - 33$)
3. **Aggregates (kg/m³):**
   - Coarse Aggregate ($800 - 1150$)
   - Fine Aggregate ($590 - 995$)
4. **Curing Conditions:**
   - Curing Age ($1 - 365\text{ Days}$)

---

## Pre-Configured Examples
- **Standard 28-Day Structural Mix:** $\approx 37.44\text{ MPa}$ (STRONG)
- **High-Performance Concrete (HPC):** $\approx 57.41\text{ MPa}$ (STRONG)
- **Fly-Ash Pozzolanic Concrete (56-Day):** $\approx 43.78\text{ MPa}$ (STRONG)
- **Lean / Low-Binder Mix (Weak):** $\approx 5.42\text{ MPa}$ (WEAK)
