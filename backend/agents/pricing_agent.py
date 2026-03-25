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
        quantity = list(quantities.values())[0] if quantities else 1

        safe_quantities = {
            "estimated_quantity": quantity if quantity else 1
        }

        # ---------------- COMPUTE PRICING ----------------
        pricing_result = compute_pricing(
            recommended_skus=sku_ids,
            quantities=safe_quantities
        )

        print("DEBUG pricing_result:", pricing_result)
        print("DEBUG type:", type(pricing_result))

        # 🔥 SAFETY CHECK
        if isinstance(pricing_result, str):
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "error": pricing_result
            }

        if not isinstance(pricing_result, list):
            raise ValueError(f"Invalid pricing output type: {type(pricing_result)}")

        # ---------------- TOTAL COST ----------------
        total_cost = sum(
            item.get("total_price", 0)
            for item in pricing_result
            if isinstance(item, dict)
        )

        # ---------------- FORMAT OUTPUT ----------------
        return {
            "pricing_details": pricing_result,
            "total_estimated_cost": total_cost
        }