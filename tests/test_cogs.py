"""Tests for the COGS (HPP) formula — the calculation most likely to be
subtly wrong per the spec (e.g. accidentally adding instead of subtracting
persediaan_akhir, or dropping a component)."""
from app.models.cogs_component import CogsComponent
from app.services.pnl_service import calculate_cogs


def test_cogs_formula_matches_spreadsheet_definition():
    component = CogsComponent(
        period="2026-03",
        persediaan_awal=1_000_000,
        pembelian_bahan_baku=5_000_000,
        ongkos_kirim=200_000,
        biaya_tenaga_kerja=1_500_000,
        biaya_overhead=300_000,
        biaya_kemasan=100_000,
        persediaan_akhir=800_000,
    )
    # goods available for the period minus what's left at the end
    expected = 1_000_000 + 5_000_000 + 200_000 + 1_500_000 + 300_000 + 100_000 - 800_000
    assert calculate_cogs(component) == expected


def test_cogs_is_zero_when_all_components_are_zero():
    component = CogsComponent(period="2026-04")
    assert calculate_cogs(component) == 0


def test_higher_closing_inventory_reduces_cogs():
    """A larger persediaan_akhir means more goods are still on hand (not
    sold), so COGS for the period should be lower — this catches a sign
    error on the subtraction if one were introduced."""
    base = CogsComponent(period="2026-05", pembelian_bahan_baku=1_000_000, persediaan_akhir=100_000)
    higher_closing = CogsComponent(period="2026-05", pembelian_bahan_baku=1_000_000, persediaan_akhir=400_000)
    assert calculate_cogs(higher_closing) < calculate_cogs(base)
