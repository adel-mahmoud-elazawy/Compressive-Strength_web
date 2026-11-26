import importlib
import os

import pytest

import app.config as config


@pytest.fixture(autouse=True)
def _reset_config():
    yield
    os.environ.pop("CORS_ORIGINS", None)
    importlib.reload(config)


def test_default_cors_origins_exclude_wildcard(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    reloaded = importlib.reload(config)

    assert reloaded.CORS_ORIGINS == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_wildcard_origin_disables_credentials(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " * ")

    reloaded = importlib.reload(config)

    assert reloaded.CORS_ORIGINS == ["*"]
    assert reloaded.CORS_ALLOW_CREDENTIALS is False


def test_origin_list_trims_whitespace(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " https://a.example , https://b.example ")

    reloaded = importlib.reload(config)

    assert reloaded.CORS_ORIGINS == [
        "https://a.example",
        "https://b.example",
    ]
    assert reloaded.CORS_ALLOW_CREDENTIALS is True
