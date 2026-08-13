"""API-level tests for the sales router: CRUD happy path plus the
future-dated-entry business rule (_reject_future_date)."""
from datetime import UTC, datetime, timedelta


def test_requires_auth(client):
    response = client.get("/api/v1/sales")
    assert response.status_code == 401


def test_create_list_get_update_delete_sale(client, auth_headers):
    create_payload = {"source": "Marketplace A", "date": "2026-03-01", "amount": 250_000}
    created = client.post("/api/v1/sales", json=create_payload, headers=auth_headers)
    assert created.status_code == 201
    sale_id = created.json()["id"]

    listed = client.get("/api/v1/sales", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/sales/{sale_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["source"] == "Marketplace A"

    updated = client.patch(
        f"/api/v1/sales/{sale_id}", json={"amount": 300_000}, headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 300_000

    deleted = client.delete(f"/api/v1/sales/{sale_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/sales/{sale_id}", headers=auth_headers).status_code == 404


def test_create_sale_rejects_future_date(client, auth_headers):
    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/sales",
        json={"source": "Marketplace A", "date": tomorrow, "amount": 100},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_sale_rejects_future_date(client, auth_headers):
    created = client.post(
        "/api/v1/sales",
        json={"source": "Marketplace A", "date": "2026-03-01", "amount": 100},
        headers=auth_headers,
    )
    sale_id = created.json()["id"]

    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()
    response = client.patch(
        f"/api/v1/sales/{sale_id}", json={"date": tomorrow}, headers=auth_headers
    )
    assert response.status_code == 400
