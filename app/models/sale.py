"""Sales — revenue entries by source/product, with date and amount."""
from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Nullable FK: the spreadsheet's Penjualan sheet has some rows keyed by a
    # free-text "source" (e.g. marketplace name) rather than a catalog
    # product, so we keep both a soft `source` label and an optional link to
    # a real product for reporting/joins when known.
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
