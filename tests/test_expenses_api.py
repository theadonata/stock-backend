"""API-level tests for the expenses router: CRUD happy path plus the
future-dated-entry business rule (_reject_future_date)."""
from datetime import UTC, datetime, timedelta


def test_requires_auth(client):
    response = client.get("/api/v1/expenses")
    assert response.status_code == 401


def test_create_list_get_update_delete_expense(client, auth_headers):
    create_payload = {"category": "Rent", "date": "2026-03-01", "amount": 1_500_000}
    created = client.post("/api/v1/expenses", json=create_payload, headers=auth_headers)
    assert created.status_code == 201
    expense_id = created.json()["id"]

    listed = client.get("/api/v1/expenses", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["category"] == "Rent"

    updated = client.patch(
        f"/api/v1/expenses/{expense_id}", json={"amount": 2_000_000}, headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 2_000_000

    deleted = client.delete(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers).status_code == 404


def test_create_expense_rejects_future_date(client, auth_headers):
    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/expenses",
        json={"category": "Rent", "date": tomorrow, "amount": 100},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_expense_rejects_future_date(client, auth_headers):
    created = client.post(
        "/api/v1/expenses",
        json={"category": "Rent", "date": "2026-03-01", "amount": 100},
        headers=auth_headers,
    )
    expense_id = created.json()["id"]

    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()
    response = client.patch(
        f"/api/v1/expenses/{expense_id}", json={"date": tomorrow}, headers=auth_headers
    )
    assert response.status_code == 400
