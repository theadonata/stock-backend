"""Product catalog — replaces hardcoded product rows in the old spreadsheet."""
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # e.g. "pcs", "roll" — free text unit label, mirrors the spreadsheet's
    # per-product unit column rather than a fixed enum, since the business
    # deals in varied units across product types.
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    # Stored as Numeric (not float) to avoid floating-point rounding errors
    # accumulating across currency calculations.
    purchase_price_per_unit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    ledger_entries = relationship("InventoryLedger", back_populates="product")
