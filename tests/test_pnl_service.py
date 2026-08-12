"""Tests for P&L aggregation across a period — matching sales/expenses to
the right month and combining with COGS, per the spec's testing focus."""
from datetime import date

from app.models.cogs_component import CogsComponent
from app.models.expense import Expense
from app.models.sale import Sale
from app.services.pnl_service import calculate_pnl


def _seed_period(db_session):
    # Two sales in March, one in April (should be excluded from a March report).
    db_session.add_all(
        [
            Sale(source="Shopee", date=date(2026, 3, 5), amount=500_000),
            Sale(source="Tokopedia", date=date(2026, 3, 20), amount=300_000),
            Sale(source="Shopee", date=date(2026, 4, 1), amount=999_999),
        ]
    )
    # One expense in March, one in April.
    db_session.add_all(
        [
            Expense(category="Listrik", date=date(2026, 3, 10), amount=100_000),
            Expense(category="Sewa", date=date(2026, 4, 2), amount=999_999),
        ]
    )
    db_session.add(
        CogsComponent(
            period="2026-03",
            persediaan_awal=0,
            pembelian_bahan_baku=200_000,
            ongkos_kirim=0,
            biaya_tenaga_kerja=0,
            biaya_overhead=0,
            biaya_kemasan=0,
            persediaan_akhir=0,
        )
    )
    db_session.commit()


def test_pnl_only_includes_the_requested_period(db_session):
    _seed_period(db_session)
    result = calculate_pnl(db_session, "2026-03")

    assert result.total_sales == 800_000  # 500k + 300k, April sale excluded
    assert result.cogs == 200_000
    assert result.gross_profit == 600_000  # 800k - 200k
    assert result.total_expenses == 100_000
    assert result.net_profit == 500_000  # 600k - 100k


def test_pnl_defaults_cogs_to_zero_when_no_components_entered(db_session):
    db_session.add(Sale(source="Shopee", date=date(2026, 6, 1), amount=100_000))
    db_session.commit()

    result = calculate_pnl(db_session, "2026-06")
    assert result.cogs == 0
    assert result.gross_profit == 100_000
