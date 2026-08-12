"""
P&L (Laba Rugi) computation.

Deliberately not a stored table (per spec) — always computed on demand from
sales, cogs_components, and expenses for a given period, so there's exactly
one source of truth per input and no risk of a stale cached P&L row.
"""
from fastapi import HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.cogs_component import CogsComponent
from app.models.expense import Expense
from app.models.sale import Sale
from app.schemas.pnl import PnlResponse


def calculate_cogs(component: CogsComponent) -> float:
    """
    COGS = opening inventory + everything added to produce goods during the
    period - closing inventory.

    This is the standard "goods available for sale minus what's left"
    formula, itemized into the categories the business already tracks
    (raw materials, freight-in, direct labor, overhead, packaging) so the
    inputs map 1:1 to the spreadsheet's HPP sheet. Isolated in its own
    function so the same formula is used everywhere COGS is needed (the
    per-period endpoint and the P&L aggregation) and is independently
    testable.
    """
    # `or 0` guards against None: the model's `default=0` only applies once
    # a row is actually flushed/inserted, so an in-memory CogsComponent
    # that hasn't been committed yet (or a row with a legitimately absent
    # value) would otherwise blow up this arithmetic with a TypeError.
    return float(
        (component.persediaan_awal or 0)
        + (component.pembelian_bahan_baku or 0)
        + (component.ongkos_kirim or 0)
        + (component.biaya_tenaga_kerja or 0)
        + (component.biaya_overhead or 0)
        + (component.biaya_kemasan or 0)
        - (component.persediaan_akhir or 0)
    )


def calculate_pnl(db: Session, period: str) -> PnlResponse:
    """Compute Laba Rugi for a "YYYY-MM" period.

    gross_profit = total_sales - cogs
    net_profit   = gross_profit - total_expenses

    Sales/expenses are matched to the period by calendar month (they're
    stored as real dates); cogs_components is matched by its own `period`
    column since it's entered at month granularity already.
    """
    try:
        year_str, month_str = period.split("-")
        year, month = int(year_str), int(month_str)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="period must be in YYYY-MM format"
        ) from exc

    total_sales = float(
        db.query(func.coalesce(func.sum(Sale.amount), 0))
        .filter(extract("year", Sale.date) == year, extract("month", Sale.date) == month)
        .scalar()
        or 0
    )

    total_expenses = float(
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(extract("year", Expense.date) == year, extract("month", Expense.date) == month)
        .scalar()
        or 0
    )

    cogs_component = db.query(CogsComponent).filter(CogsComponent.period == period).first()
    # If no COGS breakdown has been entered for the period yet, treat COGS
    # as 0 rather than erroring — a business may want to check sales/expenses
    # for a month before its HPP figures are entered.
    cogs = calculate_cogs(cogs_component) if cogs_component else 0.0

    gross_profit = total_sales - cogs
    net_profit = gross_profit - total_expenses

    return PnlResponse(
        period=period,
        total_sales=total_sales,
        cogs=cogs,
        gross_profit=gross_profit,
        total_expenses=total_expenses,
        net_profit=net_profit,
    )
