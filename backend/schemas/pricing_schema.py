from pydantic import BaseModel
from typing import Dict


class SKUCost(BaseModel):
    unit_price: float
    quantity: int
    total: float


class PricingOutput(BaseModel):
    sku_costs: Dict[str, SKUCost]
    total_estimated_cost: float