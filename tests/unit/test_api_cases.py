from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_list_cases_returns_six():
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()["cases"]
    assert len(cases) == 6
    assert {c["case_id"] for c in cases} == {"C001", "C002", "C003", "C004", "C005", "C006"}


def test_case_detail_includes_extraction_and_evidence():
    response = client.get("/api/cases/C001")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["customer_name"] == "Maya Haddad"
    assert body["evidence"], "expected at least one evidence item"
    # C001 has a receipt, so extraction should run and recover the serial number.
    serial = body["extraction"]["fields"]["serial_number"]
    assert serial["value"] == "NPX1-A101"
    assert serial["status"] == "accepted"


def test_unknown_case_returns_404():
    assert client.get("/api/cases/CXXX").status_code == 404


def test_config_reports_provider_mode():
    body = client.get("/api/config").json()
    assert body["provider_mode"] in {"azure", "local", "mock"}
