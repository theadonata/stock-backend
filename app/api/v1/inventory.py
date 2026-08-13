"""Inventory ledger: record movements, query current/point-in-time stock."""
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.inventory_ledger import InventoryLedger
from app.schemas.inventory import (
    InventoryMovementCreate,
    InventoryMovementRead,
    StockLevelResponse,
)
from app.services.inventory_service import get_stock_as_of, record_movement

router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)])


@router.post("/movements", response_model=InventoryMovementRead, status_code=status.HTTP_201_CREATED)
def create_movement(payload: InventoryMovementCreate, db: Session = Depends(get_db)) -> InventoryLedger:
    # All business-rule validation (stock-below-zero, future-dated) lives in
    # the service, which raises HTTPException directly — nothing to do here.
    return record_movement(db, payload)


@router.get("/movements", response_model=list[InventoryMovementRead])
def list_movements(product_id: int | None = None, db: Session = Depends(get_db)) -> list[InventoryLedger]:
    query = db.query(InventoryLedger).order_by(InventoryLedger.timestamp.desc())
    if product_id is not None:
        query = query.filter(InventoryLedger.product_id == product_id)
    return query.all()


@router.get("/stock/{product_id}", response_model=StockLevelResponse)
def get_stock(product_id: int, as_of: datetime | None = None, db: Session = Depends(get_db)) -> StockLevelResponse:
    """Current stock if `as_of` is omitted, else stock at that point in
    time — same derivation, just a different upper bound on the sum."""

    effective_as_of = as_of or datetime.now(UTC)
    quantity = get_stock_as_of(db, product_id, as_of=effective_as_of)
    return StockLevelResponse(product_id=product_id, as_of=effective_as_of, quantity_on_hand=quantity)
