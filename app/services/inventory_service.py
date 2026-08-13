"""
Inventory business logic: recording movements and deriving stock levels
from the ledger.

Why derive stock instead of storing it: the spec calls for both a "current
stock" figure and historical point-in-time snapshots (e.g. "stock at end of
March"). A single mutable counter can only ever answer the first question,
and it can silently drift from reality (a missed decrement, a double
increment) with no way to audit *why* the number is wrong. Summing signed
ledger rows makes stock a pure function of the audit trail: correct by
construction, and any past snapshot is just the same sum with a tighter
time filter.
"""
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.inventory_ledger import InventoryLedger, MovementDirection
from app.models.product import Product
from app.schemas.inventory import InventoryMovementCreate


def get_stock_as_of(db: Session, product_id: int, as_of: datetime | None = None) -> float:
    """Sum all ledger movements for a product up to (and including) `as_of`
    (defaults to now), treating IN as +quantity and OUT as -quantity."""
    as_of = as_of or datetime.now(UTC)

    # SQL CASE/WHEN flips the sign based on direction so the database does
    # the arithmetic in one pass instead of pulling every row into Python.
    signed_quantity = case(
        (InventoryLedger.direction == MovementDirection.IN, InventoryLedger.quantity),
        else_=-InventoryLedger.quantity,
    )
    total = (
        db.query(func.coalesce(func.sum(signed_quantity), 0))
        .filter(InventoryLedger.product_id == product_id, InventoryLedger.timestamp <= as_of)
        .scalar()
    )
    return float(total or 0)


def record_movement(db: Session, movement_in: InventoryMovementCreate) -> InventoryLedger:
    """Validate and persist a stock movement.

    Business rules enforced here (per spec's error-handling section — these
    are business-rule checks, not shape validation, so they live in the
    service layer rather than in the Pydantic schema):
      - product must exist
      - timestamp must not be in the future
      - an OUT movement must not push stock below zero
    """
    product = db.query(Product).filter(Product.id == movement_in.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    timestamp = movement_in.timestamp or datetime.now(UTC)
    now = datetime.now(UTC)
    # Normalize naive datetimes (no tzinfo) to UTC before comparing, since a
    # client might send a timestamp without an offset.
    compare_ts = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=UTC)
    if compare_ts > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Movement timestamp cannot be in the future"
        )

    if movement_in.direction == MovementDirection.OUT:
        current_stock = get_stock_as_of(db, movement_in.product_id, as_of=now)
        if movement_in.quantity > current_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock: requested {movement_in.quantity}, "
                    f"only {current_stock} on hand"
                ),
            )

    entry = InventoryLedger(
        product_id=movement_in.product_id,
        quantity=movement_in.quantity,
        direction=movement_in.direction,
        timestamp=timestamp,
        note=movement_in.note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
