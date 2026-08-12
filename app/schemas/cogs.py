"""Request/response shapes for cogs_components (HPP)."""
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CogsComponentBase(BaseModel):
    # "YYYY-MM" — validated with a regex so bad period strings (e.g. a full
    # date, or "2026/03") are rejected at the API boundary rather than
    # silently stored and breaking period lookups later.
    period: str = Field(min_length=7, max_length=7)
    persediaan_awal: float = Field(ge=0, default=0)
    pembelian_bahan_baku: float = Field(ge=0, default=0)
    ongkos_kirim: float = Field(ge=0, default=0)
    biaya_tenaga_kerja: float = Field(ge=0, default=0)
    biaya_overhead: float = Field(ge=0, default=0)
    biaya_kemasan: float = Field(ge=0, default=0)
    persediaan_akhir: float = Field(ge=0, default=0)

    @field_validator("period")
    @classmethod
    def validate_period_format(cls, value: str) -> str:
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
            raise ValueError("period must be in YYYY-MM format")
        return value


class CogsComponentCreate(CogsComponentBase):
    pass


class CogsComponentUpdate(BaseModel):
    persediaan_awal: float | None = Field(default=None, ge=0)
    pembelian_bahan_baku: float | None = Field(default=None, ge=0)
    ongkos_kirim: float | None = Field(default=None, ge=0)
    biaya_tenaga_kerja: float | None = Field(default=None, ge=0)
    biaya_overhead: float | None = Field(default=None, ge=0)
    biaya_kemasan: float | None = Field(default=None, ge=0)
    persediaan_akhir: float | None = Field(default=None, ge=0)


class CogsComponentRead(CogsComponentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
