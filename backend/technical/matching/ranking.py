from backend.technical.matching.spec_match import compute_spec_match


def rank_skus_by_spec_match(rfp_spec: dict, skus: list, top_k: int = 3):
    """
    Rank SKUs based on spec match %.

    Returns:
    - Top K SKUs
    - Each SKU contains:
        sku_id
        match %
        price
        explanation
    """

    ranked_results = []

    for sku in skus:

        sku_id = sku.get("sku_id")
        sku_specs = sku.get("specs", {})
        price = sku.get("price", None)

        # 🚫 Skip invalid SKUs
        if not sku_specs:
            continue

        score, explanation = compute_spec_match(rfp_spec, sku_specs)

        ranked_results.append({
            "sku_id": sku_id,
            "spec_match_percent": score,
            "price": price,
            "explanation": explanation
        })

    # --- Sorting Logic ---
    # 1. Higher match %
    # 2. Lower price (if available)

    ranked_results.sort(
        key=lambda x: (
            -x["spec_match_percent"],
            float(x["price"]) if x["price"] is not None else float("inf")
        )
    )

    return ranked_results[:top_k]