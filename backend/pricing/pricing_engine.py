import pandas as pd
from pathlib import Path


# ---------------- PATH ----------------
PRICING_TABLE_PATH = Path("data/pricing.csv")


# ---------------- LOAD TABLE ----------------
def load_pricing_table() -> pd.DataFrame:
    """
    Load SKU pricing table.
    """
    if not PRICING_TABLE_PATH.exists():
        raise FileNotFoundError("Pricing table not found at data/pricing.csv")

    return pd.read_csv(PRICING_TABLE_PATH)


# ---------------- COMPUTE PRICING ----------------
def compute_pricing(recommended_skus: list, quantities: dict) -> dict:
    """
    Calculate total estimated cost using realistic pricing columns.
    """

    pricing_table = load_pricing_table()

    sku_costs = {}
    total_cost = 0

    for sku in recommended_skus:

        price_row = pricing_table[pricing_table["sku_id"] == sku]

        if price_row.empty:
            material = 0
            testing = 0
            insulation = 0
            manufacturing = 0
            final_price = 0
        else:
            row = price_row.iloc[0]

            material = float(row.get("material_cost", 0))
            testing = float(row.get("testing_cost", 0))
            insulation = float(row.get("insulation_cost", 0))
            manufacturing = float(row.get("manufacturing_cost", 0))
            final_price = float(row.get("final_price_per_meter", 0))

        qty = quantities.get("estimated_quantity", 1)
        if not qty:
            qty = 1
        total = final_price * qty

        sku_costs[sku] = {
            "material_cost": material,
            "testing_cost": testing,
            "insulation_cost": insulation,
            "manufacturing_cost": manufacturing,
            "unit_price": final_price,
            "quantity": qty,
            "total": total
        }

        total_cost += total

    pricing_list = []

    for sku, details in sku_costs.items():
        pricing_list.append({
            "sku_id": sku,
            "material_cost": details["material_cost"],
            "testing_cost": details["testing_cost"],
            "insulation_cost": details["insulation_cost"],
            "manufacturing_cost": details["manufacturing_cost"],
            "unit_price": details["unit_price"],
            "quantity": details["quantity"],
            "total_price": details["total"]
        })

    return pricing_list