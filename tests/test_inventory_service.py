"""
Tests for the running stock balance derived from the inventory ledger —
called out in the spec as logic "most likely to be subtly wrong" (sign
errors, off-by-time-window bugs, stock-below-zero not being caught).
"""
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.models.inventory_ledger import MovementDirection
from app.models.product import Product
from app.schemas.inventory import InventoryMovementCreate
from app.services.inventory_service import get_stock_as_of, record_movement


def _make_product(db_session) -> Product:
    product = Product(name="Croco Nocturne Bag", unit="pcs", purchase_price_per_unit=100000)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_stock_starts_at_zero(db_session):
    product = _make_product(db_session)
    assert get_stock_as_of(db_session, product.id) == 0


def test_stock_in_then_out_nets_correctly(db_session):
    product = _make_product(db_session)
    record_movement(
        db_session, InventoryMovementCreate(product_id=product.id, quantity=10, direction=MovementDirection.IN)
    )
    record_movement(
        db_session, InventoryMovementCreate(product_id=product.id, quantity=3, direction=MovementDirection.OUT)
    )
    assert get_stock_as_of(db_session, product.id) == 7


def test_stock_out_cannot_exceed_current_stock(db_session):
    """Core business rule from the spec: an OUT movement that would push
    stock below zero must be rejected."""
    product = _make_product(db_session)
    record_movement(
        db_session, InventoryMovementCreate(product_id=product.id, quantity=5, direction=MovementDirection.IN)
    )
    with pytest.raises(HTTPException) as exc_info:
        record_movement(
            db_session,
            InventoryMovementCreate(product_id=product.id, quantity=6, direction=MovementDirection.OUT),
        )
    assert exc_info.value.status_code == 400


def test_future_dated_movement_is_rejected(db_session):
    product = _make_product(db_session)
    future_ts = datetime.now(UTC) + timedelta(days=1)
    with pytest.raises(HTTPException) as exc_info:
        record_movement(
            db_session,
            InventoryMovementCreate(
                product_id=product.id, quantity=1, direction=MovementDirection.IN, timestamp=future_ts
            ),
        )
    assert exc_info.value.status_code == 400


def test_point_in_time_stock_ignores_later_movements(db_session):
    """Historical stock snapshot: summing up to a past timestamp should not
    include movements recorded after that point."""
    product = _make_product(db_session)
    now = datetime.now(UTC)
    earlier = now - timedelta(days=5)

    record_movement(
        db_session,
        InventoryMovementCreate(
            product_id=product.id, quantity=10, direction=MovementDirection.IN, timestamp=earlier
        ),
    )
    # This second movement happens "now" — a snapshot taken right after the
    # first movement should not see it.
    record_movement(
        db_session, InventoryMovementCreate(product_id=product.id, quantity=4, direction=MovementDirection.IN)
    )

    snapshot_time = earlier + timedelta(hours=1)
    assert get_stock_as_of(db_session, product.id, as_of=snapshot_time) == 10
    assert get_stock_as_of(db_session, product.id) == 14
