# backend/schemas/final_response.py

from pydantic import BaseModel

from backend.schemas.sales_schema import SalesAgentOutput
from backend.schemas.technical_schema import TechnicalAgentOutput
from backend.schemas.pricing_schema import PricingOutput


class FinalRFPResponse(BaseModel):
    """
    Final orchestrated output returned to the UI.
    Combines outputs from all agents.
    """

    rfp_summary: SalesAgentOutput
    technical_summary: TechnicalAgentOutput
    pricing_summary: PricingOutput