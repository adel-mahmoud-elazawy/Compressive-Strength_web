import os
import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' can be imported anywhere
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

# Vercel entrypoint looks for 'app'
__all__ = ["app"]
