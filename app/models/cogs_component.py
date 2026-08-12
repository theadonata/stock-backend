"""
COGS (HPP) components — one row per period (month), matching the fields on
the spreadsheet's HPP sheet. COGS for the period is:

    persediaan_awal + pembelian_bahan_baku + ongkos_kirim + biaya_tenaga_kerja
    + biaya_overhead + biaya_kemasan - persediaan_akhir

i.e. "goods available for the period" (opening inventory + everything added
during production) minus "what's left at the end" (closing inventory) —
standard COGS accounting, just itemized the way the business already
tracks it in the spreadsheet. See app.services.pnl_service.calculate_cogs.
"""
from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CogsComponent(Base):
    __tablename__ = "cogs_components"
    # One COGS breakdown per period — prevents accidentally double-entering
    # a month's HPP figures.
    __table_args__ = (UniqueConstraint("period", name="uq_cogs_components_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Stored as "YYYY-MM" text (not a Date) since these are month-level
    # inputs, not a specific day — matches the spreadsheet's monthly HPP
    # columns.
    period: Mapped[str] = mapped_column(String(7), nullable=False, index=True)

    persediaan_awal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    pembelian_bahan_baku: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    ongkos_kirim: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    biaya_tenaga_kerja: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    biaya_overhead: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    biaya_kemasan: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    persediaan_akhir: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
