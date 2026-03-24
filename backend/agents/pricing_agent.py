# backend/agents/pricing_agent.py

from backend.pricing.pricing_engine import compute_pricing


class PricingAgent:

    def run(self, technical_output: dict, quantities: dict) -> dict:
        """
        Entry point for Pricing Agent.

        Inputs:
            technical_output → from Technical Agent
            quantities → from RFP parser

        Output:
            pricing summary (JSON-safe)
        """

        # ---------------- EXTRACT SKU IDs ----------------
        recommended = technical_output.get("recommended_skus", [])

        if not recommended:
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "message": "No SKUs available for pricing"
            }

        # Extract SKU IDs
        sku_ids = [item["sku_id"] for item in recommended]

        # ---------------- SAFE QUANTITY ----------------
        quantity = quantities.get("estimated_quantity", 1)

        safe_quantities = {
            "estimated_quantity": quantity if quantity else 1
        }

        # ---------------- COMPUTE PRICING ----------------
        pricing_result = compute_pricing(
            recommended_skus=sku_ids,
            quantities=safe_quantities
        )

        # ---------------- TOTAL COST ----------------
        total_cost = sum(item["total_price"] for item in pricing_result)

        # ---------------- FORMAT OUTPUT ----------------
        return {
            "pricing_details": pricing_result,
            "total_estimated_cost": total_cost
        }