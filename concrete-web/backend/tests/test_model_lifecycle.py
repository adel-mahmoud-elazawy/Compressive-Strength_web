import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.config import MODEL_PATH
from app.errors import ModelUnavailableError, PredictionError
from app.model import ConcreteModelManager
from app.schemas import ConcreteMixInput

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_import_succeeds_when_model_bundle_missing(tmp_path):
    env = os.environ.copy()
    env["MODEL_PATH"] = str(tmp_path / "missing.pkl")

    result = subprocess.run(
        [sys.executable, "-c", "import app.model"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_constructor_does_not_load_model(tmp_path):
    try:
        manager = ConcreteModelManager(model_file_path=str(tmp_path / "missing.pkl"))
    except FileNotFoundError:
        pytest.fail("constructor must not load the model bundle")

    assert manager.is_loaded is False


def test_load_model_reports_failure_without_raising(tmp_path):
    manager = ConcreteModelManager(model_file_path=str(tmp_path / "missing.pkl"))

    assert manager.load_model() is False
    assert manager.is_loaded is False
    assert manager.load_error is not None


def test_load_model_succeeds_with_real_bundle():
    manager = ConcreteModelManager(model_file_path=MODEL_PATH)

    assert manager.load_model() is True
    assert manager.is_loaded is True
    assert manager.load_error is None


def test_predict_raises_typed_error_when_model_unavailable(tmp_path):
    try:
        manager = ConcreteModelManager(model_file_path=str(tmp_path / "missing.pkl"))
    except FileNotFoundError:
        pytest.fail("constructor must not load the model bundle")

    with pytest.raises(ModelUnavailableError):
        manager.predict(ConcreteMixInput())


def test_predict_wraps_inference_failure_in_typed_error(monkeypatch):
    manager = ConcreteModelManager(model_file_path=MODEL_PATH)
    assert manager.load_model() is True

    def explode(_features):
        raise RuntimeError("boom")

    monkeypatch.setattr(manager.regressor, "predict", explode)

    with pytest.raises(PredictionError):
        manager.predict(ConcreteMixInput())


def test_corrupt_model_bundle_is_recorded_not_raised(tmp_path):
    corrupt = tmp_path / "corrupt.pkl"
    corrupt.write_bytes(b"\x80\x04garbage")
    manager = ConcreteModelManager(model_file_path=str(corrupt))

    assert manager.load_model() is False
    assert manager.is_loaded is False
    assert ":" in manager.load_error
    assert manager.load_error.split(":", 1)[0].endswith("Error")
