"""API-level tests for the inventory router: record a movement, list
movements, and read stock level -- exercising get_stock's `as_of` default
(the line changed in this PR: `datetime.now(UTC)` instead of the old
inline `from datetime import timezone` + `timezone.utc`)."""
from app.models.product import Product


def _make_product(db_session) -> Product:
    product = Product(name="Widget", unit="pcs", purchase_price_per_unit=1000)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_requires_auth(client):
    response = client.get("/api/v1/inventory/movements")
    assert response.status_code == 401


def test_create_and_list_movement(client, db_session, auth_headers):
    product = _make_product(db_session)

    created = client.post(
        "/api/v1/inventory/movements",
        json={"product_id": product.id, "quantity": 10, "direction": "in"},
        headers=auth_headers,
    )
    assert created.status_code == 201
    assert created.json()["direction"] == "in"

    listed = client.get("/api/v1/inventory/movements", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_get_stock_defaults_as_of_to_now(client, db_session, auth_headers):
    product = _make_product(db_session)
    client.post(
        "/api/v1/inventory/movements",
        json={"product_id": product.id, "quantity": 10, "direction": "in"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/inventory/movements",
        json={"product_id": product.id, "quantity": 3, "direction": "out"},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/inventory/stock/{product.id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["quantity_on_hand"] == 7
    assert body["as_of"] is not None
