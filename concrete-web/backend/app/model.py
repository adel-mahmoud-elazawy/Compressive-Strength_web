import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from app.config import MODEL_PATH
from app.schemas import ConcreteMixInput, PredictionResponse, MetaResponse, FieldMeta, MixExample

# ---------------------------------------------------------------------------
# Exact feature engineering function from training & UI notebook
# ---------------------------------------------------------------------------
def add_features(data: pd.DataFrame) -> pd.DataFrame:
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


class ConcreteModelManager:
    """Singleton-style manager that loads the model bundle once on startup."""

    def __init__(self, model_file_path: str = MODEL_PATH):
        self.model_path = model_file_path
        self.regressor = None
        self.classifier = None
        self.cutoff: float = 33.72
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model bundle file not found at: {self.model_path}. "
                "Ensure concrete_model.pkl is placed in the backend directory."
            )
        
        bundle = joblib.load(self.model_path)
        self.regressor = bundle["regressor"]
        self.classifier = bundle.get("classifier", None)
        self.cutoff = float(bundle["cutoff"])
        self.is_loaded = True

        print(f"[ModelManager] Loaded model bundle: {os.path.basename(self.model_path)}")
        print(f"[ModelManager] Regressor: {type(self.regressor).__name__}, Cutoff: {self.cutoff:.2f} MPa")

    def predict(self, mix_input: ConcreteMixInput) -> PredictionResponse:
        if not self.is_loaded:
            self.load_model()

        # Build raw DataFrame in exact feature order
        raw_dict = {
            "Cement": float(mix_input.Cement),
            "Blast_Furnace_Slag": float(mix_input.Blast_Furnace_Slag),
            "Fly_Ash": float(mix_input.Fly_Ash),
            "Water": float(mix_input.Water),
            "Superplasticizer": float(mix_input.Superplasticizer),
            "Coarse_Aggregate": float(mix_input.Coarse_Aggregate),
            "Fine_Aggregate": float(mix_input.Fine_Aggregate),
            "Age": float(mix_input.Age),
        }
        df_raw = pd.DataFrame([raw_dict])
        df_featured = add_features(df_raw)

        # Regression prediction
        predicted_strength = float(self.regressor.predict(df_featured)[0])

        # Classification decision
        if self.classifier is None:
            is_strong = predicted_strength >= self.cutoff
        else:
            is_strong = bool(self.classifier.predict(df_featured)[0] == 1)

        label = "STRONG" if is_strong else "WEAK"
        wc_ratio = float(df_featured["Water_Cement_Ratio"].iloc[0])
        wb_ratio = float(df_featured["Water_Binder_Ratio"].iloc[0])
        total_binder = float(df_featured["Binder"].iloc[0])
        psi = predicted_strength * 145.038

        return PredictionResponse(
            predicted_strength_mpa=round(predicted_strength, 2),
            label=label,
            cutoff_mpa=round(self.cutoff, 2),
            is_strong=is_strong,
            equivalent_psi=round(psi, 0),
            water_cement_ratio=round(wc_ratio, 2),
            water_binder_ratio=round(wb_ratio, 2),
            total_binder_kg_m3=round(total_binder, 1),
            curing_age_days=float(mix_input.Age)
        )

    def get_meta(self) -> MetaResponse:
        fields = [
            FieldMeta(
                name="Cement",
                label="Cement",
                unit="kg/m³",
                min=100.0,
                max=540.0,
                default=280.0,
                step=1.0,
                category="Binder Materials",
                description="Standard Portland cement content"
            ),
            FieldMeta(
                name="Blast_Furnace_Slag",
                label="Blast Furnace Slag",
                unit="kg/m³",
                min=0.0,
                max=360.0,
                default=0.0,
                step=1.0,
                category="Binder Materials",
                description="Granulated blast-furnace slag (SCM)"
            ),
            FieldMeta(
                name="Fly_Ash",
                label="Fly Ash",
                unit="kg/m³",
                min=0.0,
                max=200.0,
                default=0.0,
                step=1.0,
                category="Binder Materials",
                description="Pozzolanic mineral admixture from coal combustion"
            ),
            FieldMeta(
                name="Water",
                label="Water",
                unit="kg/m³",
                min=120.0,
                max=250.0,
                default=180.0,
                step=1.0,
                category="Water & Additives",
                description="Mixing water content"
            ),
            FieldMeta(
                name="Superplasticizer",
                label="Superplasticizer",
                unit="kg/m³",
                min=0.0,
                max=33.0,
                default=0.0,
                step=0.1,
                category="Water & Additives",
                description="High-range water-reducing chemical admixture"
            ),
            FieldMeta(
                name="Coarse_Aggregate",
                label="Coarse Aggregate",
                unit="kg/m³",
                min=800.0,
                max=1150.0,
                default=970.0,
                step=1.0,
                category="Aggregates",
                description="Coarse gravel and crushed rock skeleton"
            ),
            FieldMeta(
                name="Fine_Aggregate",
                label="Fine Aggregate",
                unit="kg/m³",
                min=590.0,
                max=995.0,
                default=780.0,
                step=1.0,
                category="Aggregates",
                description="Natural sand / fine matrix filler"
            ),
            FieldMeta(
                name="Age",
                label="Curing Age",
                unit="Days",
                min=1.0,
                max=365.0,
                default=28.0,
                step=1.0,
                category="Curing Age",
                description="Moist curing period prior to compression test"
            ),
        ]

        examples = [
            MixExample(
                name="Standard 28-Day Structural Mix",
                description="Balanced structural grade concrete cured for standard 28-day testing.",
                tag="Standard",
                expected_label="STRONG",
                values={
                    "Cement": 280.0,
                    "Blast_Furnace_Slag": 100.0,
                    "Fly_Ash": 0.0,
                    "Water": 180.0,
                    "Superplasticizer": 5.0,
                    "Coarse_Aggregate": 970.0,
                    "Fine_Aggregate": 770.0,
                    "Age": 28.0
                }
            ),
            MixExample(
                name="High-Performance Concrete (HPC)",
                description="Low water-binder ratio with slag and superplasticizer for high compressive resistance.",
                tag="High-Performance",
                expected_label="STRONG",
                values={
                    "Cement": 380.0,
                    "Blast_Furnace_Slag": 95.0,
                    "Fly_Ash": 0.0,
                    "Water": 165.0,
                    "Superplasticizer": 8.5,
                    "Coarse_Aggregate": 960.0,
                    "Fine_Aggregate": 810.0,
                    "Age": 28.0
                }
            ),
            MixExample(
                name="Fly-Ash Pozzolanic Concrete (56-Day)",
                description="Long-term pozzolanic hydration mix incorporating fly ash for sustainable strength.",
                tag="Pozzolanic",
                expected_label="STRONG",
                values={
                    "Cement": 250.0,
                    "Blast_Furnace_Slag": 0.0,
                    "Fly_Ash": 125.0,
                    "Water": 175.0,
                    "Superplasticizer": 5.0,
                    "Coarse_Aggregate": 990.0,
                    "Fine_Aggregate": 760.0,
                    "Age": 56.0
                }
            ),
            MixExample(
                name="Lean / Low-Binder Mix (Weak)",
                description="Lean non-structural mixture tested at 7 days with high water-cement ratio.",
                tag="Lean / Early",
                expected_label="WEAK",
                values={
                    "Cement": 160.0,
                    "Blast_Furnace_Slag": 0.0,
                    "Fly_Ash": 0.0,
                    "Water": 205.0,
                    "Superplasticizer": 0.0,
                    "Coarse_Aggregate": 1050.0,
                    "Fine_Aggregate": 850.0,
                    "Age": 7.0
                }
            ),
        ]

        return MetaResponse(
            model_name="GradientBoostingRegressor + Median Cutoff Classifier",
            cutoff_mpa=round(self.cutoff, 2),
            fields=fields,
            examples=examples
        )


# Global instance
model_manager = ConcreteModelManager()
