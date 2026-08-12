"""Request/response shapes for the inventory ledger."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory_ledger import MovementDirection


class InventoryMovementCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="Always positive; direction determines sign.")
    direction: MovementDirection
    # Optional: defaults to "now" in the service layer if omitted. Allowing
    # a caller-supplied timestamp lets staff log a movement after the fact
    # (e.g. entering yesterday's stock count), but future timestamps are
    # rejected by the service per the spec's business-rule validation.
    timestamp: datetime | None = None
    note: str | None = Field(default=None, max_length=500)


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: float
    direction: MovementDirection
    timestamp: datetime
    note: str | None = None


class StockLevelResponse(BaseModel):
    product_id: int
    # as_of is echoed back so the caller can confirm what point in time the
    # figure reflects (current stock uses "now").
    as_of: datetime
    quantity_on_hand: float
