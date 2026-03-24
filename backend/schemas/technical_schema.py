# backend/schemas/technical_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class CableAttributes(BaseModel):
    """
    Optional technical attributes extracted from RFP or SKU datasheets.
    """
    core_count: Optional[int] = None
    cross_section_mm2: Optional[float] = None
    armouring: Optional[str] = None


class RFPSpec(BaseModel):
    """
    Normalized representation of RFP technical requirements.
    Used as input to the Technical Agent.
    """

    rfp_id: str = Field(..., min_length=3)

    voltage: Optional[str] = None
    material: Optional[str] = None
    insulation: Optional[str] = None
    standard: Optional[str] = None

    attributes: CableAttributes = CableAttributes()


class SKUSpec(BaseModel):
    """
    Normalized representation of an OEM SKU.
    Extracted from datasheets.
    """

    sku_id: str = Field(..., min_length=2)

    voltage: Optional[str] = None
    material: Optional[str] = None
    insulation: Optional[str] = None
    standard: Optional[str] = None

    attributes: CableAttributes = CableAttributes()

    source_document: str
    extraction_method: str = "deterministic"


class TechnicalAgentOutput(BaseModel):
    """
    Final output produced by the Technical Agent.
    Sent to the Pricing Agent and Orchestrator.
    """

    recommended_skus: List[str]

    spec_match_scores: Dict[str, float]

    comparison_table: List[Dict]