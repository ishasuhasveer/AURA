from pydantic import BaseModel, Field
from typing import Dict


class SKUCost(BaseModel):
    """
    Cost breakdown for a single SKU.
    """

    sku_id: str = Field(..., min_length=2)
    unit_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    total: float = Field(..., ge=0)


class PricingOutput(BaseModel):
    """
    Final output returned by the Pricing Agent.
    """

    sku_costs: Dict[str, SKUCost]

    total_estimated_cost: float = Field(..., ge=0)