"""
test_api.py — API endpoint tests using FastAPI's TestClient.

Every endpoint added in Phase 1 is covered here.
Tests run against a fresh in-memory SQLite database — never touches finance.db.

Run with:
    pytest test_api.py -v
"""
from __future__ import annotations

import os
import pytest
import tempfile

# Point to a temp DB before importing anything that touches the database
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["SQLITE_FILE"] = _tmp.name
os.environ["DATABASE_URL"] = ""   # force SQLite mode

from fastapi.testclient import TestClient
import db_connection
import database
from api import app

# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def fresh_db(monkeypatch, tmp_path):
    """Each test gets its own empty database."""
    db_file = str(tmp_path / "api_test.db")
    monkeypatch.setattr(db_connection, "SQLITE_FILE", db_file)
    database.init_db()
    database.init_events_table()


@pytest.fixture
def client():
    return TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:

    def test_health_returns_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ── State ─────────────────────────────────────────────────────────────────────

class TestState:

    def test_state_returns_all_fields(self, client):
        r = client.get("/api/state")
        assert r.status_code == 200
        data = r.json()
        for key in ("balance", "weekly_income", "weekly_expenses",
                    "net_weekly_flow", "savings_rate", "risk_score", "health_score"):
            assert key in data

    def test_state_default_balance_is_zero(self, client):
        r = client.get("/api/state")
        assert r.json()["balance"] == 0.0


# ── Balance ───────────────────────────────────────────────────────────────────

class TestBalance:

    def test_update_balance(self, client):
        r = client.put("/api/balance", json={"amount": 500.0})
        assert r.status_code == 200
        assert r.json()["balance"] == 500.0

    def test_updated_balance_reflected_in_state(self, client):
        client.put("/api/balance", json={"amount": 750.0})
        r = client.get("/api/state")
        assert r.json()["balance"] == 750.0

    def test_negative_balance_rejected(self, client):
        r = client.put("/api/balance", json={"amount": -1.0})
        assert r.status_code == 422   # pydantic validation (ge=0)

    def test_zero_balance_accepted(self, client):
        r = client.put("/api/balance", json={"amount": 0.0})
        assert r.status_code == 200


# ── Jobs ──────────────────────────────────────────────────────────────────────

class TestJobs:

    def test_list_jobs_empty(self, client):
        r = client.get("/api/jobs")
        assert r.status_code == 200
        assert r.json() == []

    def test_add_job(self, client):
        r = client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        assert r.status_code == 201
        assert r.json()["name"] == "Barista"

    def test_add_job_appears_in_list(self, client):
        client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        r = client.get("/api/jobs")
        assert len(r.json()) == 1

    def test_add_duplicate_job_rejected(self, client):
        client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        r = client.post("/api/jobs", json={"name": "Barista", "amount": 200, "frequency": "Weekly"})
        assert r.status_code == 400

    def test_delete_job(self, client):
        client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        r = client.delete("/api/jobs/Barista")
        assert r.status_code == 200

    def test_delete_job_removes_from_list(self, client):
        client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        client.delete("/api/jobs/Barista")
        r = client.get("/api/jobs")
        assert r.json() == []

    def test_delete_nonexistent_job_returns_404(self, client):
        r = client.delete("/api/jobs/Ghost")
        assert r.status_code == 404

    def test_update_job(self, client):
        client.post("/api/jobs", json={"name": "Barista", "amount": 300, "frequency": "Weekly"})
        r = client.put("/api/jobs/Barista", json={"name": "Barista", "amount": 350, "frequency": "Weekly"})
        assert r.status_code == 200
        assert r.json()["amount"] == 350

    def test_update_nonexistent_job_returns_404(self, client):
        r = client.put("/api/jobs/Ghost", json={"name": "Ghost", "amount": 100, "frequency": "Weekly"})
        assert r.status_code == 404


# ── Expenses ──────────────────────────────────────────────────────────────────

class TestExpenses:

    def test_list_expenses_empty(self, client):
        r = client.get("/api/expenses")
        assert r.status_code == 200
        assert r.json() == []

    def test_add_expense(self, client):
        r = client.post("/api/expenses", json={
            "name": "Rent", "amount": 700, "category": "Housing",
            "date": "2026-01-01", "frequency": "Monthly"
        })
        assert r.status_code == 201
        assert r.json()["name"] == "Rent"

    def test_add_expense_appears_in_list(self, client):
        client.post("/api/expenses", json={
            "name": "Rent", "amount": 700, "category": "Housing",
            "date": "2026-01-01", "frequency": "Monthly"
        })
        r = client.get("/api/expenses")
        assert len(r.json()) == 1

    def test_delete_expense(self, client):
        client.post("/api/expenses", json={
            "name": "Rent", "amount": 700, "category": "Housing",
            "date": "2026-01-01", "frequency": "Monthly"
        })
        r = client.delete("/api/expenses/Rent")
        assert r.status_code == 200

    def test_delete_nonexistent_expense_returns_404(self, client):
        r = client.delete("/api/expenses/Ghost")
        assert r.status_code == 404

    def test_update_expense(self, client):
        client.post("/api/expenses", json={
            "name": "Rent", "amount": 700, "category": "Housing",
            "date": "2026-01-01", "frequency": "Monthly"
        })
        r = client.put("/api/expenses/Rent", json={
            "name": "Rent", "amount": 800, "category": "Housing",
            "date": "2026-01-01", "frequency": "Monthly"
        })
        assert r.status_code == 200
        assert r.json()["amount"] == 800


# ── Projection ────────────────────────────────────────────────────────────────

class TestProjection:

    def test_projection_default_12_weeks(self, client):
        r = client.get("/api/projection")
        assert r.status_code == 200
        assert len(r.json()["timeline"]) == 12

    def test_projection_custom_weeks(self, client):
        r = client.get("/api/projection?weeks=4")
        assert len(r.json()["timeline"]) == 4

    def test_projection_has_required_fields(self, client):
        r = client.get("/api/projection")
        data = r.json()
        assert "starting_balance" in data
        assert "net_weekly_flow" in data
        assert "timeline" in data

    def test_projection_weeks_out_of_range(self, client):
        r = client.get("/api/projection?weeks=999")
        assert r.status_code == 400


# ── Insights ──────────────────────────────────────────────────────────────────

class TestInsights:

    def test_insights_returns_scores(self, client):
        r = client.get("/api/insights")
        assert r.status_code == 200
        data = r.json()
        assert "health_score" in data
        assert "risk_score" in data
        assert "insights" in data

    def test_insights_list_is_list(self, client):
        r = client.get("/api/insights")
        assert isinstance(r.json()["insights"], list)


# ── History ───────────────────────────────────────────────────────────────────

class TestHistory:

    def test_history_returns_count_and_snapshots(self, client):
        r = client.get("/api/history")
        assert r.status_code == 200
        data = r.json()
        assert "count" in data
        assert "snapshots" in data

    def test_history_snapshots_is_list(self, client):
        r = client.get("/api/history")
        assert isinstance(r.json()["snapshots"], list)


# ── Simulation ────────────────────────────────────────────────────────────────

class TestSimulation:

    def test_monte_carlo(self, client):
        r = client.post("/api/simulate/monte-carlo", json={"weeks": 4, "n": 50})
        assert r.status_code == 200
        data = r.json()
        assert "average" in data
        assert "deficit_probability" in data

    def test_whatif(self, client):
        r = client.post("/api/simulate/whatif", json={
            "description": "Car repair", "dollar_change": -400, "weeks": 4
        })
        assert r.status_code == 200
        assert "history" in r.json()
