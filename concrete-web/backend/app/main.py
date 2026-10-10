from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.schemas import ConcreteMixInput, PredictionResponse, MetaResponse
from app.model import model_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure model is pre-loaded
    if not model_manager.is_loaded:
        model_manager.load_model()
    yield

app = FastAPI(
    title="Concrete Compressive Strength API",
    description="Machine Learning REST API for predicting concrete compressive strength (MPa) and quality classification.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True if CORS_ORIGINS != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    """Returns server and ML model operational status."""
    return {
        "status": "healthy",
        "service": "concrete-strength-api",
        "model_loaded": model_manager.is_loaded,
        "cutoff_mpa": round(model_manager.cutoff, 2)
    }

@app.get("/meta", response_model=MetaResponse, tags=["Metadata"])
def get_metadata():
    """Returns mixture input field bounds, defaults, units, categories, and preset examples."""
    return model_manager.get_meta()

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_concrete_strength(mix_input: ConcreteMixInput):
    """
    Accepts 8 concrete mix parameters, executes feature engineering, and returns
    predicted compressive strength in MPa along with STRONG/WEAK classification.
    """
    try:
        return model_manager.predict(mix_input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
