"""
Inventory ledger — one row per stock movement.

Current stock is deliberately NOT a stored column anywhere. It's derived by
summing signed quantities from this ledger (see
app.services.inventory_service.get_current_stock). This mirrors real-world
bookkeeping (a running ledger of movements) rather than a mutable "current
stock" counter, which would drift from reality if any write were missed,
double-applied, or reordered — and it lets us answer "what was stock on
2026-03-31?" for free by summing up to a timestamp, matching the spec's
requirement for historical point-in-time stock snapshots.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MovementDirection(str, enum.Enum):
    IN = "in"
    OUT = "out"


class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    # Always a positive quantity; `direction` determines whether it adds to
    # or subtracts from stock. Keeping quantity unsigned (rather than
    # negative-for-out) makes the ledger easier for a human to read.
    quantity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    # values_callable: store the enum's *value* ("in"/"out", matching the
    # Postgres enum type created in the migration) rather than SQLAlchemy's
    # default of storing the member *name* ("IN"/"OUT") — without this the
    # DB rejects every insert with "invalid input value for enum".
    direction: Mapped[MovementDirection] = mapped_column(
        Enum(MovementDirection, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    product = relationship("Product", back_populates="ledger_entries")
