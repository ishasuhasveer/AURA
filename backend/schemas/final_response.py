from pydantic import BaseModel
from typing import Dict, Any


class FinalRFPResponse(BaseModel):

    rfp_summary: Dict[str, Any]
    technical_summary: Dict[str, Any]
    pricing_summary: Dict[str, Any]