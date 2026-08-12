"""Request/response shapes for the expenses resource."""
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    category: str = Field(min_length=1, max_length=255)
    date: date_type
    amount: float = Field(gt=0)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=255)
    date: date_type | None = None
    amount: float | None = Field(default=None, gt=0)


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
