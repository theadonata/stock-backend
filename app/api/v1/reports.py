"""Reporting endpoints — currently just the P&L (Laba Rugi) report, computed
on the fly per the spec (no stored P&L table)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.pnl import PnlResponse
from app.services.pnl_service import calculate_pnl

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


@router.get("/pnl", response_model=PnlResponse)
def get_pnl(period: str, db: Session = Depends(get_db)) -> PnlResponse:
    """period is "YYYY-MM", e.g. ?period=2026-03."""
    return calculate_pnl(db, period)
