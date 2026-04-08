from backend.technical.matching.spec_match import compute_spec_match


def rank_skus_by_spec_match(rfp_spec: dict, skus: list, top_k: int = 3):

    ranked_results = []

    for sku in skus:
        sku_specs = sku.get("specs", {})   # ✅ FIX HERE

        score, explanation = compute_spec_match(rfp_spec, sku_specs)

        ranked_results.append({
            "sku_id": sku.get("sku_id"),
            "spec_match_percent": score,
            "explanation": explanation
        })

    ranked_results.sort(
        key=lambda x: x["spec_match_percent"],
        reverse=True
    )

    return ranked_results[:top_k]