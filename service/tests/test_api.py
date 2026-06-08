import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app

JWT_SECRET = "test-secret"
AGENCY = "agency-demo-001"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.settings.settings.jwt_secret", JWT_SECRET)
    monkeypatch.setattr("app.settings.settings.service_auth_token", "test-service-token")
    return TestClient(app)


def _token(roles: list[str] | None = None) -> str:
    return jwt.encode(
        {
            "sub": "user-001",
            "agency_id": AGENCY,
            "roles": roles or ["dispatcher"],
            "exp": int(time.time()) + 3600,
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "bluecore-ai-addon"


def test_assistant_requires_auth(client):
    response = client.post(
        "/v1/assistant/chat",
        json={"agency_id": AGENCY, "prompt": "Summarize active calls"},
    )
    assert response.status_code == 401


def test_assistant_chat(client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", JWT_SECRET)
    response = client.post(
        "/v1/assistant/chat",
        json={"agency_id": AGENCY, "prompt": "Subject with weapon reported", "command": "general"},
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "weapon" in body["officer_safety_flags"]
    assert body["requires_human_review"] is True


def test_threat_assessment_critical(client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", JWT_SECRET)
    response = client.post(
        "/v1/threat/assess",
        json={
            "agency_id": AGENCY,
            "person_records": [
                {
                    "id": "p1",
                    "indicators": ["assault_on_officer", "active_warrant_violent"],
                    "summary": "Prior assault and active warrant",
                }
            ],
            "incident_context": {"weapons_involved": True},
        },
        headers={"Authorization": f"Bearer {_token(['officer'])}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in ("elevated_risk", "critical_officer_safety_alert")
    assert len(body["contributing_factors"]) >= 2
    assert body["officer_notification"] is not None
    assert "disclaimer" in body
