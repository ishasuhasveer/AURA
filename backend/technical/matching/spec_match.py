from backend.technical.matching.similarity import (
    exact_match,
    numeric_match
)


def compute_spec_match(rfp_spec: dict, sku_spec: dict):
    """
    Compare RFP specs with SKU specs.

    Returns:
    - match percentage
    - detailed explanation (with gaps)
    """

    total = 0
    matched = 0
    explanation = {}

    # --- Merge top-level + attributes ---
    def flatten(spec):
        flat = {}

        for key, value in spec.items():
            if key == "attributes" and isinstance(value, dict):
                for k, v in value.items():
                    flat[k] = v
            else:
                flat[key] = value

        return flat

    rfp_flat = flatten(rfp_spec)
    sku_flat = flatten(sku_spec)

    for key, rfp_value in rfp_flat.items():

        # Ignore unspecified fields
        if rfp_value is None:
            continue

        total += 1
        sku_value = sku_flat.get(key)

        # Decide comparator
        if isinstance(rfp_value, (int, float)):
            score = numeric_match(rfp_value, sku_value)
        else:
            score = exact_match(rfp_value, sku_value)

        # Convert None → skip
        if score is None:
            total -= 1
            continue

        matched += score

        # --- Gap detection ---
        if score == 1:
            gap = "Match"
        elif score == 0.5:
            gap = "Partial match / Over-spec"
        else:
            if sku_value is None:
                gap = "Missing in SKU"
            else:
                gap = "Mismatch"

        explanation[key] = {
            "rfp": rfp_value,
            "sku": sku_value,
            "score": score,
            "gap": gap
        }

    percent = (matched / total) * 100 if total > 0 else 0

    return round(percent, 2), explanation