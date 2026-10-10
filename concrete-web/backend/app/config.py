import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "concrete_model.pkl"))

# CORS settings
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,*"
).split(",")
