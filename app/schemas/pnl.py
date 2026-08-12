"""Response shape for the computed P&L (Laba Rugi) report. Not backed by a
table — see app.services.pnl_service."""
from pydantic import BaseModel


class PnlResponse(BaseModel):
    period: str
    total_sales: float
    cogs: float
    gross_profit: float
    total_expenses: float
    net_profit: float
