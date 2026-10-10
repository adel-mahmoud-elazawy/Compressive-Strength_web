from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConcreteMixInput(BaseModel):
    """Raw 8 mix ingredients with operational bounds derived from dataset distribution."""
    Cement: float = Field(
        280.0,
        ge=100.0,
        le=540.0,
        description="Portland cement content in kg/m^3 (Range: 100 - 540)"
    )
    Blast_Furnace_Slag: float = Field(
        0.0,
        ge=0.0,
        le=360.0,
        description="Granulated blast-furnace slag in kg/m^3 (Range: 0 - 360)"
    )
    Fly_Ash: float = Field(
        0.0,
        ge=0.0,
        le=200.0,
        description="Pozzolanic fly ash in kg/m^3 (Range: 0 - 200)"
    )
    Water: float = Field(
        180.0,
        ge=120.0,
        le=250.0,
        description="Batch mixing water in kg/m^3 (Range: 120 - 250)"
    )
    Superplasticizer: float = Field(
        0.0,
        ge=0.0,
        le=33.0,
        description="High-range water reducer in kg/m^3 (Range: 0.0 - 33.0)"
    )
    Coarse_Aggregate: float = Field(
        970.0,
        ge=800.0,
        le=1150.0,
        description="Gravel and crushed stone in kg/m^3 (Range: 800 - 1150)"
    )
    Fine_Aggregate: float = Field(
        780.0,
        ge=590.0,
        le=995.0,
        description="Natural sand / fine matrix filler in kg/m^3 (Range: 590 - 995)"
    )
    Age: float = Field(
        28.0,
        ge=1.0,
        le=365.0,
        description="Curing period in days prior to test (Range: 1 - 365)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "Cement": 380.0,
                "Blast_Furnace_Slag": 95.0,
                "Fly_Ash": 0.0,
                "Water": 165.0,
                "Superplasticizer": 8.5,
                "Coarse_Aggregate": 960.0,
                "Fine_Aggregate": 810.0,
                "Age": 28.0
            }
        }
    }


class PredictionResponse(BaseModel):
    """Comprehensive prediction response payload."""
    predicted_strength_mpa: float = Field(..., description="Estimated compressive strength in MPa")
    label: str = Field(..., description="Quality classification: STRONG or WEAK")
    cutoff_mpa: float = Field(..., description="Benchmark cutoff threshold in MPa")
    is_strong: bool = Field(..., description="True if predicted strength meets or exceeds cutoff")
    equivalent_psi: float = Field(..., description="Converted strength in pounds per square inch (psi)")
    water_cement_ratio: float = Field(..., description="Water-to-cement ratio (w/c)")
    water_binder_ratio: float = Field(..., description="Water-to-binder ratio (w/b)")
    total_binder_kg_m3: float = Field(..., description="Total binder content (Cement + Slag + Fly Ash) in kg/m^3")
    curing_age_days: float = Field(..., description="Curing age in days")


class FieldMeta(BaseModel):
    name: str
    label: str
    unit: str
    min: float
    max: float
    default: float
    step: float
    category: str
    description: str


class MixExample(BaseModel):
    name: str
    description: str
    tag: str
    expected_label: str
    values: Dict[str, float]


class MetaResponse(BaseModel):
    model_name: str
    cutoff_mpa: float
    fields: List[FieldMeta]
    examples: List[MixExample]
