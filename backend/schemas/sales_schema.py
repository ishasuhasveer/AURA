# backend/schemas/sales_schema.py

from pydantic import BaseModel, Field
from typing import Literal

class SalesAgentOutput(BaseModel):
    rfp_id: str = Field(..., min_length=3)
    deadline: str = Field(..., min_length=3)
    scope_summary: str = Field(..., min_length=3)
    priority: Literal["high", "medium", "low"]
    @classmethod
    def validate_output(cls, data: dict):
        return cls(**data)
