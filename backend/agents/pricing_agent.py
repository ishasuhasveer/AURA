# backend/agents/pricing_agent.py

from backend.pricing.pricing_engine import compute_pricing
from backend.database.mongo_client import db


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

        # Handle both formats safely
        if isinstance(recommended, list) and len(recommended) > 0:

            if isinstance(recommended[0], str):
                sku_ids = recommended

            elif isinstance(recommended[0], dict):
                sku_ids = [
                    item.get("sku_id")
                    for item in recommended
                    if isinstance(item, dict) and "sku_id" in item
                ]

            else:
                raise ValueError(f"Unexpected SKU format: {type(recommended[0])}")

        else:
            sku_ids = []

        print("DEBUG SKU IDS:", sku_ids)

        # ---------------- FETCH SKU OBJECTS FROM DB ----------------
        raw_skus = list(db["products"].find({
            "sku_id": {"$in": sku_ids}
        }))

        # 🔥 FIX: Deduplicate by sku_id (keep first occurrence)
        unique_skus = {}
        for sku in raw_skus:
            sid = sku.get("sku_id")
            if sid not in unique_skus:
                unique_skus[sid] = sku

        sku_objects = list(unique_skus.values())

        print("DEBUG SKU OBJECTS:", sku_objects)

        # 🚨 SAFETY CHECK
        if not sku_objects:
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "error": "No matching SKU objects found in DB"
            }

        # ---------------- SAFE QUANTITY ----------------
        quantity = next(iter(quantities.values()), 1)
        if not quantity:
            quantity = 1
        quantity = quantity if quantity else 1

        # Map quantity per SKU (engine expects sku_id mapping)
        safe_quantities = {
            sku.get("sku_id"): quantity
            for sku in sku_objects
        }

        print("DEBUG FINAL QUANTITIES:", safe_quantities)

        # ---------------- COMPUTE PRICING ----------------
        pricing_result = compute_pricing(
            sku_objects,
            safe_quantities
        )

        print("DEBUG pricing_result:", pricing_result)
        print("DEBUG type:", type(pricing_result))

        # ---------------- SAFETY CHECK ----------------
        if isinstance(pricing_result, str):
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "error": pricing_result
            }

        # ⚠️ IMPORTANT: your engine returns dict, not list
        if isinstance(pricing_result, dict):
            return pricing_result

        raise ValueError(f"Invalid pricing output type: {type(pricing_result)}")