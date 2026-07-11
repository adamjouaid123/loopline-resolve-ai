from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import settings


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["provider"] == settings.app_provider_mode
