import logging
import math
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import CORS_ALLOW_CREDENTIALS, CORS_ORIGINS
from app.errors import ModelUnavailableError, PredictionError
from app.schemas import ConcreteMixInput, PredictionResponse, MetaResponse
from app.model import model_manager

logger = logging.getLogger(__name__)


def _cors_headers(request) -> dict[str, str]:
    """CORS headers for responses produced outside CORSMiddleware."""
    origin = request.headers.get("origin")
    if not origin:
        return {}
    if "*" in CORS_ORIGINS:
        return {"Access-Control-Allow-Origin": "*"}
    if origin not in CORS_ORIGINS:
        return {}
    headers = {"Access-Control-Allow-Origin": origin, "Vary": "Origin"}
    if CORS_ALLOW_CREDENTIALS:
        headers["Access-Control-Allow-Credentials"] = "true"
    return headers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load once. Failure is recorded, not raised, so the service
    # can start and report an unavailable model through its endpoints.
    model_manager.load_model()
    yield

app = FastAPI(
    title="Concrete Compressive Strength API",
    description="Machine Learning REST API for predicting concrete compressive strength (MPa) and quality classification.",
    version="1.0.0",
    lifespan=lifespan
)


def _json_safe(value: Any) -> Any:
    """Replace non-finite floats so validation errors stay JSON serializable."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Keep the standard 422 shape; sanitize rejected non-finite inputs."""
    return JSONResponse(
        status_code=422,
        content={"detail": [_json_safe(error) for error in exc.errors()]},
    )


@app.exception_handler(ModelUnavailableError)
async def model_unavailable_handler(request, exc: ModelUnavailableError):
    """Model not loaded: safe 503, details stay in the server log."""
    logger.warning("Model unavailable: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Model is not available"},
    )


@app.exception_handler(PredictionError)
async def prediction_error_handler(request, exc: PredictionError):
    """Inference failed: log the cause, return a generic message."""
    logger.exception("Prediction failed: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Prediction failed due to an internal error"},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request, exc: Exception):
    """Last-resort handler: never echo internal exception text to clients."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers(request),
    )


# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
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

@app.get("/ready", tags=["System"])
def readiness_check():
    """Readiness probe. Unlike the legacy /health, this fails when the model is missing."""
    if not model_manager.is_loaded:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "model_loaded": False},
        )
    return {"status": "ready", "model_loaded": True}


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
    return model_manager.predict(mix_input)
