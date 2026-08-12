"""Request/response shapes for the products resource."""
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    unit: str = Field(min_length=1, max_length=32)
    # gt=0 enforced here (Pydantic validation) rather than in the DB, so bad
    # input is rejected with a clean 422 before it ever reaches a query.
    purchase_price_per_unit: float = Field(gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    unit: str | None = Field(default=None, min_length=1, max_length=32)
    purchase_price_per_unit: float | None = Field(default=None, gt=0)


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
