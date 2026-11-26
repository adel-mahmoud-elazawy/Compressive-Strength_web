import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import ConcreteMixInput


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_schema_rejects_non_finite_inputs(bad_value):
    with pytest.raises(ValidationError):
        ConcreteMixInput(Cement=bad_value)


def test_api_rejects_overflowing_json_number():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            content=b'{"Cement": 1e999}',
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 422


def test_schema_accepts_valid_defaults():
    mix = ConcreteMixInput()

    assert mix.Cement == 280.0
    assert mix.Age == 28.0
