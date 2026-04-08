from backend.technical.matching.similarity import (
    exact_match,
    numeric_match
)


def compute_spec_match(rfp_spec: dict, sku_spec: dict):
    """
    Compare RFP specs with SKU specs.
    Returns:
    - match %
    - detailed explanation
    """

    total = len(rfp_spec)
    matched = 0
    explanation = {}

    for key, rfp_value in rfp_spec.items():

        sku_value = sku_spec.get(key)

        if sku_value is None:
            score = 0

        elif isinstance(rfp_value, (int, float)):
            diff = abs(rfp_value - sku_value)

            if diff == 0:
                score = 1
            elif diff <= 0.1 * rfp_value:
                score = 0.5
            else:
                score = 0

        else:
            score = 1 if rfp_value == sku_value else 0

        matched += score

        explanation[key] = {
            "rfp": rfp_value,
            "sku": sku_value,
            "score": score
        }

    percent = (matched / total) * 100 if total > 0 else 0

    return percent, explanation