import base64

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.auth import BasicAuthSettings, create_basic_auth_middleware


def test_basic_auth_settings_require_both_values(monkeypatch):
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "user")
    monkeypatch.delenv("BASIC_AUTH_PASSWORD", raising=False)

    with pytest.raises(RuntimeError):
        BasicAuthSettings.from_env()


def test_basic_auth_settings_disabled_without_env(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USERNAME", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASSWORD", raising=False)

    settings = BasicAuthSettings.from_env()

    assert settings.enabled is False


def test_basic_auth_blocks_requests_without_credentials():
    app = FastAPI()
    settings = BasicAuthSettings(username="n8n", password="secret")
    app.middleware("http")(create_basic_auth_middleware(settings))

    @app.get("/secured")
    async def secured():
        return {"ok": True}

    client = TestClient(app)

    response = client.get("/secured")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == 'Basic realm="Kleinanzeigen API"'


def test_basic_auth_allows_correct_credentials():
    app = FastAPI()
    settings = BasicAuthSettings(username="n8n", password="secret")
    app.middleware("http")(create_basic_auth_middleware(settings))

    @app.get("/secured")
    async def secured():
        return {"ok": True}

    client = TestClient(app)
    token = base64.b64encode(b"n8n:secret").decode("ascii")

    response = client.get("/secured", headers={"Authorization": f"Basic {token}"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}
