"""Request/response shapes for the sales resource."""
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field


class SaleBase(BaseModel):
    source: str = Field(min_length=1, max_length=255)
    product_id: int | None = None
    date: date_type
    amount: float = Field(gt=0)


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    source: str | None = Field(default=None, min_length=1, max_length=255)
    product_id: int | None = None
    date: date_type | None = None
    amount: float | None = Field(default=None, gt=0)


class SaleRead(SaleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
