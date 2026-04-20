def make_decision(technical: dict, pricing: dict) -> list:
    """
    Decision Engine

    Combines:
    - Technical match %
    - Pricing

    Returns:
    Ranked list of SKU decisions
    """

    results = []

    pricing_list = pricing.get("pricing_details", [])

    if not isinstance(pricing_list, list):
        pricing_list = []

    scores = {}

    # --------------------------------------------------
    # 🔥 STEP 1: EXTRACT FROM requirements_mapping
    # --------------------------------------------------

    for req in technical.get("requirements_mapping", []):
        for sku in req.get("top_matches", []):

            sku_config_id = sku.get("sku_config_id")
            match = sku.get("match_percent", 0)

            if not sku_config_id:
                continue

            # Keep best match per config
            if sku_config_id not in scores or scores[sku_config_id] < match:
                scores[sku_config_id] = match

    if not scores:
        return []

    # --------------------------------------------------
    # 🔥 STEP 2: BUILD DECISIONS
    # --------------------------------------------------

    for sku_config_id, spec_match in scores.items():

        # 🔍 Find pricing
        price_data = next(
            (p for p in pricing_list if p.get("sku_config_id") == sku_config_id),
            None
        )

        total_price = price_data.get("total_price", 0) if price_data else 0

        # ---------------- DECISION LOGIC ----------------
        price_penalty = total_price * 0.0001  # 🔥 tuned down
        final_score = spec_match - price_penalty

        # ---------------- EXPLANATION ----------------
        explanation = []

        if spec_match >= 90:
            explanation.append("High technical compliance")
        elif spec_match >= 70:
            explanation.append("Moderate technical compliance")
        else:
            explanation.append("Low technical compliance")

        if total_price == 0:
            explanation.append("Pricing unavailable")
        elif total_price < 100000:
            explanation.append("Cost-effective option")
        else:
            explanation.append("Higher cost option")

        # ---------------- BUILD RESULT ----------------
        results.append({
            "sku_config_id": sku_config_id,
            "spec_match": spec_match,
            "total_price": total_price,
            "final_score": round(final_score, 2),
            "explanation": explanation
        })

    # --------------------------------------------------
    # 🔥 STEP 3: SORT
    # --------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["final_score"],
        reverse=True
    )

    # --------------------------------------------------
    # 🔥 STEP 4: ADD RANK
    # --------------------------------------------------

    for idx, item in enumerate(results):
        item["rank"] = idx + 1

    return results