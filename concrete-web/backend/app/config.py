import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "concrete_model.pkl"))

# CORS settings. Wildcard is opt-in only: it must be requested explicitly
# because it disables credentialed requests.
DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


def _parse_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


CORS_ORIGINS = _parse_origins(os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS))
CORS_ALLOW_CREDENTIALS = "*" not in CORS_ORIGINS
