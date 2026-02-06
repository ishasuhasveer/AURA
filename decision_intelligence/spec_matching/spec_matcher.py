from decision_intelligence.spec_matching.comparators import (
    exact_match,
    numeric_match
)


def compute_spec_match(rfp_spec: dict, sku: dict):
    """
    Compute Spec Match % between one RFP specification
    and one OEM SKU.

    Returns:
    - spec_match_percent (float)
    - explanation (list of dicts)
    """

    scores = []
    explanation = []

    # --------------------------------------------------
    # 1. Mandatory specifications (hard requirements)
    # --------------------------------------------------
    mandatory_fields = [
        "voltage",
        "conductor",
        "insulation",
        "standard"
    ]

    for field in mandatory_fields:
        rfp_value = rfp_spec.get(field)
        sku_value = sku.get(field)

        score = exact_match(rfp_value, sku_value)

        # Only evaluate if RFP specified the field
        if score is not None:
            scores.append(score)
            explanation.append({
                "spec": field,
                "category": "mandatory",
                "rfp_value": rfp_value,
                "sku_value": sku_value,
                "score": score
            })

    # --------------------------------------------------
    # 2. Optional specifications (scoring preferences)
    # --------------------------------------------------
    rfp_attrs = rfp_spec.get("attributes", {})
    sku_attrs = sku.get("attributes", {})

    for attr, rfp_value in rfp_attrs.items():
        if rfp_value is None:
            continue

        sku_value = sku_attrs.get(attr)

        if isinstance(rfp_value, (int, float)):
            score = numeric_match(rfp_value, sku_value)
        else:
            score = exact_match(rfp_value, sku_value)

        scores.append(score)
        explanation.append({
            "spec": attr,
            "category": "optional",
            "rfp_value": rfp_value,
            "sku_value": sku_value,
            "score": score
        })

    # --------------------------------------------------
    # 3. Final Spec Match %
    # --------------------------------------------------
    if not scores:
        spec_match_percent = 0.0
    else:
        spec_match_percent = round((sum(scores) / len(scores)) * 100, 2)

    return spec_match_percent, explanation
