import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]
VALID_MIX = {
    "Cement": 280.0,
    "Blast_Furnace_Slag": 100.0,
    "Fly_Ash": 0.0,
    "Water": 180.0,
    "Superplasticizer": 5.0,
    "Coarse_Aggregate": 970.0,
    "Fine_Aggregate": 770.0,
    "Age": 28.0,
}


def test_unexpected_prediction_error_hides_internal_detail(monkeypatch):
    def explode(_mix):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(main_module.model_manager, "predict", explode)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/predict", json=VALID_MIX)

    assert response.status_code == 500
    assert "secret internal detail" not in response.text


def test_model_unavailable_returns_generic_503(monkeypatch):
    monkeypatch.setattr(main_module.model_manager, "is_loaded", False)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/predict", json=VALID_MIX)

    assert response.status_code == 503
    assert response.json() == {"detail": "Model is not available"}


def test_health_reports_unloaded_model(monkeypatch):
    monkeypatch.setattr(main_module.model_manager, "is_loaded", False)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["model_loaded"] is False


def test_allowed_origin_receives_cors_header():
    client = TestClient(app)

    response = client.get(
        "/health", headers={"Origin": "http://localhost:3000"}
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_unlisted_origin_receives_no_cors_header():
    client = TestClient(app)

    response = client.get(
        "/health", headers={"Origin": "https://evil.example"}
    )

    assert "access-control-allow-origin" not in response.headers


def test_vercel_entrypoint_exposes_app_from_other_cwd(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)

    result = subprocess.run(
        [sys.executable, "-c", "from api.index import app; print(app.title)"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Concrete Compressive Strength API"


def test_generic_500_keeps_cors_headers_for_allowed_origin(monkeypatch):
    def explode(_mix):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(main_module.model_manager, "predict", explode)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/predict",
        json=VALID_MIX,
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_ready_returns_200_when_model_is_loaded():
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "model_loaded": True}


def test_ready_returns_503_when_model_is_unloaded(monkeypatch):
    monkeypatch.setattr(main_module.model_manager, "is_loaded", False)
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "model_loaded": False}


def test_wildcard_cors_never_sends_credentials_header(tmp_path):
    script = tmp_path / "cors_probe.py"
    script.write_text(
        "from fastapi.testclient import TestClient\n"
        "from app.main import app\n"
        "r = TestClient(app).get('/health', headers={'Origin': 'https://evil.example'})\n"
        "print('ORIGIN:', r.headers.get('access-control-allow-origin'))\n"
        "print('CREDENTIALS:', r.headers.get('access-control-allow-credentials'))\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    env["CORS_ORIGINS"] = "*,https://trusted.example"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ORIGIN: https://evil.example" not in result.stdout
    assert "CREDENTIALS: None" in result.stdout
