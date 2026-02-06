from decision_intelligence.spec_matching.spec_matcher import compute_spec_match


def rank_skus_by_spec_match(rfp_spec: dict, skus: list, top_k: int = 3):
    """
    Rank OEM SKUs based on Spec Match % for a given RFP.

    Returns a list of ranked SKU results.
    """

    ranked_results = []

    for sku in skus:
        score, explanation = compute_spec_match(rfp_spec, sku)

        ranked_results.append({
            "sku_id": sku.get("sku_id"),
            "spec_match_percent": score,
            "explanation": explanation
        })

    # Sort descending by spec match %
    ranked_results.sort(
        key=lambda x: x["spec_match_percent"],
        reverse=True
    )

    return ranked_results[:top_k]
