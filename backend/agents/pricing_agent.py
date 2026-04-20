# backend/agents/pricing_agent.py

from backend.database.mongo_client import db


class PricingAgent:

    def run(self, technical_output: dict, quantities: dict) -> dict:

        # --------------------------------------------------
        # 🚨 STEP 1: BLOCK PRICING IF TECHNICAL FAILED
        # --------------------------------------------------

        if technical_output.get("error"):
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "message": "No valid SKUs for pricing (technical validation failed)"
            }

        # --------------------------------------------------
        # 🔥 STEP 2: EXTRACT SKU CONFIG IDS
        # --------------------------------------------------

        sku_config_ids = []

        if "requirements_mapping" in technical_output:

            for req in technical_output.get("requirements_mapping", []):
                for sku in req.get("top_matches", []):
                    sid = sku.get("sku_config_id")
                    if sid:
                        sku_config_ids.append(sid)

        elif "recommended_skus" in technical_output:

            recommended = technical_output.get("recommended_skus", [])

            if isinstance(recommended, list):
                for item in recommended:
                    if isinstance(item, dict):
                        sid = item.get("sku_config_id")
                        if sid:
                            sku_config_ids.append(sid)

        # Deduplicate
        sku_config_ids = list(dict.fromkeys(sku_config_ids))

        print("DEBUG SKU CONFIG IDS:", sku_config_ids)

        if not sku_config_ids:
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "message": "No SKUs available for pricing"
            }

        # --------------------------------------------------
        # 🔥 STEP 3: FETCH PRODUCTS (FOR METADATA ONLY)
        # --------------------------------------------------

        products = {
            p["sku_config_id"]: p
            for p in db["products"].find({
                "sku_config_id": {"$in": sku_config_ids}
            })
        }

        if not products:
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "error": "No matching product configs found"
            }

        # --------------------------------------------------
        # 🔥 STEP 4: FETCH PRICING (BATCH OPTIMIZATION)
        # --------------------------------------------------

        pricing_map = {
            p["sku_config_id"]: p
            for p in db["pricing_catalog"].find({
                "sku_config_id": {"$in": sku_config_ids}
            })
        }

        pricing_details = []
        total_cost = 0

        # --------------------------------------------------
        # 🔥 STEP 5: COMPUTE PRICING
        # --------------------------------------------------

        for sku_config_id in sku_config_ids:

            product = products.get(sku_config_id)
            pricing = pricing_map.get(sku_config_id)

            if not product:
                print(f"⚠️ Missing product for {sku_config_id}")
                continue

            if not pricing:
                print(f"⚠️ No pricing found for {sku_config_id}")
                continue

            price_per_meter = pricing.get("price_per_meter")

            if not price_per_meter:
                print(f"⚠️ Invalid price for {sku_config_id}")
                continue

            # --------------------------------------------------
            # 🔥 QUANTITY HANDLING (STRICT)
            # --------------------------------------------------

            quantity = quantities.get(sku_config_id)

            if quantity is None:
                print(f"⚠️ Missing quantity for {sku_config_id}, defaulting to 1")
                quantity = 1

            if quantity <= 0:
                print(f"⚠️ Invalid quantity for {sku_config_id}, defaulting to 1")
                quantity = 1

            total_price = price_per_meter * quantity

            pricing_details.append({
                "sku_config_id": sku_config_id,
                "sku_name": product.get("sku_name"),
                "unit_type": "meter",
                "quantity": quantity,
                "price_per_meter": price_per_meter,
                "total_price": total_price
            })

            total_cost += total_price

        # --------------------------------------------------
        # 🚨 STEP 6: FINAL VALIDATION
        # --------------------------------------------------

        if not pricing_details:
            return {
                "pricing_details": [],
                "total_estimated_cost": 0,
                "error": "No pricing could be computed"
            }

        return {
            "pricing_details": pricing_details,
            "total_estimated_cost": total_cost,
            "status": "success"
        }