from typing import Any
from backend.database.mongo_client import db


# ---------------- APPLY RULES ----------------
def apply_pricing_rules(base_price: float, sku: dict) -> float:
    """
    Apply pricing rules in controlled + deterministic way
    """

    specs = sku.get("specs", {})
    product_type = specs.get("product_type")

    rules = list(db["pricing_rules"].find())

    final_price = base_price

    # 🔥 Sort rules for deterministic application
    # Product-specific first, then global
    rules = sorted(
        rules,
        key=lambda r: 0 if r.get("product_type") != "ALL" else 1
    )

    for rule in rules:

        rule_type = rule.get("rule_type")
        rule_product = rule.get("product_type")
        percentage = rule.get("percentage", 0)

        apply = False

        # Product-specific rule
        if rule_product == product_type:
            apply = True

        # Global rule
        elif rule_product == "ALL":
            apply = True

        if apply:
            print(f"Applying rule {rule_type}: +{percentage}%")
            final_price *= (1 + percentage / 100)

    return round(final_price, 2)


# ---------------- PRICE LOOKUP ----------------
def get_price_for_sku(sku: dict):

    specs = sku.get("specs", {})

    cross_section = specs.get("cross_section_mm2")
    cores = specs.get("cores")
    product_type = specs.get("product_type")
    cable_type = specs.get("cable_type")

    if cross_section and cores and product_type and cable_type:

        price_doc = db["pricing_catalog"].find_one({
            "cross_section_mm2": cross_section,
            "cores": float(cores),
            "product_type": product_type,
            "cable_type": cable_type
        })

        if price_doc:
            return price_doc.get("price_per_meter", 0)

        # fallback nearest
        nearest = list(db["pricing_catalog"].find({
            "cores": float(cores),
            "product_type": product_type,
            "cable_type": cable_type
        }))

        if nearest:
            closest = min(
                nearest,
                key=lambda x: abs(x["cross_section_mm2"] - cross_section)
            )
            return closest.get("price_per_meter", 0)

    print("❌ No price found for SKU:", sku.get("sku_id"))
    return 0

# ---------------- COMPUTE PRICING ----------------
def compute_pricing(sku_objects: list, quantities: dict) -> dict[str, list[Any] | int]:

    pricing_list = []
    total_cost = 0

    for sku in sku_objects:

        sku_id = sku.get("sku_id")

        qty = quantities.get(sku_id, 1)
        if not qty:
            qty = 1

        # -------- BASE PRICE --------
        base_price = get_price_for_sku(sku)

        if base_price == 0:
            print(f"⚠️ WARNING: Base price missing for {sku_id}")
            continue

        # -------- APPLY RULES --------
        final_unit_price = apply_pricing_rules(base_price, sku)

        total = final_unit_price * qty

        pricing_list.append({
            "sku_id": sku_id,
            "base_unit_price": base_price,
            "final_unit_price": final_unit_price,
            "quantity": qty,
            "total_price": total
        })

        total_cost += total

    return {
        "pricing_details": pricing_list,
        "total_estimated_cost": total_cost
    }