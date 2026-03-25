# backend/schemas/sales_schema.py

from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class SalesAgentOutput(BaseModel):
    """
    Schema for validated output produced by the Sales Agent.

    This object is consumed by the Main Orchestrator to
    decide whether downstream processing should continue.
    """

    rfp_id: str = Field(..., min_length=3, description="Unique identifier of the RFP")

    deadline: date = Field(
        ...,
        description="Submission deadline extracted from the RFP"
    )

    scope_summary: str = Field(
        ...,
        min_length=3,
        description="Short textual summary of the RFP scope"
    )

    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Priority assigned based on deadline and business relevance"
    )

    @classmethod
    def validate_output(cls, data: dict):
        """Validate raw dictionary output from the Sales Agent."""
        return cls(**data)