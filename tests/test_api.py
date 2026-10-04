"""End-to-end API tests using an isolated SQLite database."""

import os
import tempfile

os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "api_test.db")

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402


def test_calculate_history_flow():
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"

        # start from a clean database
        client.delete("/api/history")
        assert client.get("/api/history").json() == []

        # calculate on the back end
        response = client.post("/api/calculate", json={"expression": "(1+2)*3"})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["expression"] == "(1+2)*3"
        assert body["result"] == 9
        record_id = body["id"]

        # history is persisted on the back end
        history = client.get("/api/history").json()
        assert len(history) == 1
        assert history[0]["id"] == record_id
        assert history[0]["result"] == 9
        assert history[0]["created_at"]

        # delete one record
        deleted = client.delete(f"/api/history/{record_id}")
        assert deleted.status_code == 200
        assert deleted.json()["deleted"] == 1
        assert client.get("/api/history").json() == []

        # deleting a missing record -> 404
        missing = client.delete(f"/api/history/{record_id}")
        assert missing.status_code == 404
        assert missing.json()["success"] is False


def test_clear_all_history():
    with TestClient(app) as client:
        client.delete("/api/history")
        client.post("/api/calculate", json={"expression": "1+1"})
        client.post("/api/calculate", json={"expression": "2+2"})
        assert len(client.get("/api/history").json()) == 2

        cleared = client.delete("/api/history")
        assert cleared.status_code == 200
        assert cleared.json()["deleted"] == 2
        assert client.get("/api/history").json() == []


def test_error_responses():
    with TestClient(app) as client:
        invalid = client.post("/api/calculate", json={"expression": "1+"})
        assert invalid.status_code == 400
        assert invalid.json() == {"success": False, "message": "Invalid expression"}

        division = client.post("/api/calculate", json={"expression": "1/0"})
        assert division.status_code == 400
        assert division.json()["message"] == "Division by zero"

        missing_expr = client.post("/api/calculate", json={})
        assert missing_expr.status_code == 422
        assert missing_expr.json()["success"] is False
