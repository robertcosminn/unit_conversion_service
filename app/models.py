"""Pydantic & ORM models: keep the ‘M’ of MVC in one file."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ---------- SQLAlchemy table (persists every conversion) ---------- #
class ConversionLog(Base):  # noqa: D101  (flake8-docstring for brevity)
    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)  # e.g. 'length'
    src_value = Column(Float, nullable=False)
    src_unit = Column(String, nullable=False)
    dst_unit = Column(String, nullable=False)
    result = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------- Pydantic request / response schemas ---------- #
class ConversionRequest(BaseModel):
    """Input validated by Pydantic – universal for all categories."""
    category: Literal["length", "temperature", "weight"]
    value: float = Field(..., gt=0)
    from_unit: str
    to_unit: str

    model_config = {"frozen": True}          # ← makes the instance hashable ✅

    @field_validator("from_unit", "to_unit", mode="before")
    def _lower(cls, v: str) -> str:
        return v.lower()




class ConversionResponse(BaseModel):
    """Output object – what our CLI prints (could also be JSON in an API)."""

    result: float
    details: str  # e.g. "3.5 m → 11.4823 ft"
