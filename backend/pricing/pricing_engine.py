import pandas as pd
from pathlib import Path


PRICING_TABLE_PATH = Path("data/pricing_tables/cable_prices.csv")


def load_pricing_table() -> pd.DataFrame:
    """
    Load SKU pricing table.
    """
    if not PRICING_TABLE_PATH.exists():
        raise FileNotFoundError("Pricing table not found.")

    return pd.read_csv(PRICING_TABLE_PATH)


def compute_pricing(recommended_skus: list, quantities: dict) -> dict:
    """
    Calculate total estimated cost.

    Inputs:
    recommended_skus: ["SKU123", "SKU456"]
    quantities: {"SKU123": 10}

    Returns:
    {
        "sku_costs": {...},
        "total_estimated_cost": 1234
    }
    """

    pricing_table = load_pricing_table()

    sku_costs = {}
    total_cost = 0

    for sku in recommended_skus:

        price_row = pricing_table[pricing_table["sku_id"] == sku]

        if price_row.empty:
            unit_price = 0
        else:
            unit_price = float(price_row.iloc[0]["unit_price"])

        qty = quantities.get(sku, 1)

        cost = unit_price * qty

        sku_costs[sku] = {
            "unit_price": unit_price,
            "quantity": qty,
            "total": cost
        }

        total_cost += cost

    return {
        "sku_costs": sku_costs,
        "total_estimated_cost": total_cost
    }