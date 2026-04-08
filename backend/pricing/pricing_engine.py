from typing import Any
from backend.database.mongo_client import db


# ---------------- APPLY RULES ----------------
def apply_pricing_rules(base_price: float, sku: dict) -> float:
    """
    Apply pricing rules from MongoDB (pricing_rules collection)
    """

    specs = sku.get("specs", {})
    product_type = specs.get("product_type")

    rules = list(db["pricing_rules"].find())

    final_price = base_price

    for rule in rules:

        rule_type = rule.get("rule_type")
        rule_product = rule.get("product_type")
        percentage = rule.get("percentage", 0)

        # Apply product-specific rules
        if rule_product == product_type:
            final_price *= (1 + percentage / 100)

        # Apply global rules
        elif rule_product == "ALL":
            final_price *= (1 + percentage / 100)

    return final_price


# ---------------- PRICE LOOKUP ----------------
def get_price_for_sku(sku: dict):

    specs = sku.get("specs", {})

    cross_section = specs.get("cross_section_mm2")
    cores = specs.get("cores")
    product_type = specs.get("product_type")
    conductor = specs.get("conductor", "").lower()

    # ---------------- MULTICORE ----------------
    if cross_section and cores and product_type:
        price_doc = db["pricing_catalog"].find_one({
            "cross_section_mm2": cross_section,
            "cores": cores,
            "product_type": product_type
        })

        if price_doc:
            return price_doc.get("price_per_meter", 0)

    # ---------------- WIRES ----------------
    if cross_section:
        price_doc = db["pricing_catalog"].find_one({
            "cross_section_mm2": cross_section,
            "material": conductor
        })

        if price_doc:
            return price_doc.get("price_per_meter", 0)

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