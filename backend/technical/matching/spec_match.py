from backend.technical.matching.similarity import (
    exact_match,
    numeric_match
)
from backend.technical.matching.spec_mapper import map_rfp_to_product


def compute_spec_match(rfp_spec: dict, sku_spec: dict):
    """
    Compare RFP specs with SKU specs using mapping layer.

    Returns:
    - match percentage
    - detailed explanation (with gaps)
    """

    # --- Flatten helper ---
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

    # 🔥 NEW: Apply mapping layer
    mapped_specs = map_rfp_to_product(rfp_flat)

    total = 0
    matched = 0
    explanation = {}

    for target_key, meta in mapped_specs.items():

        rfp_value = meta["value"]
        match_type = meta["type"]
        source_key = meta["source"]

        # Ignore empty values
        if rfp_value is None:
            continue

        total += 1
        sku_value = sku_flat.get(target_key)

        # --- Comparator logic ---
        if sku_value is None:
            score = 0

        elif match_type == "exact":
            score = exact_match(rfp_value, sku_value)

        elif match_type == "categorical":
            if str(rfp_value).lower() in str(sku_value).lower():
                score = 0.5
            else:
                score = 0

        elif match_type == "numeric_inverse":
            try:
                if float(sku_value) <= float(rfp_value):
                    score = 1
                else:
                    score = 0
            except:
                score = 0

        else:
            # fallback
            if isinstance(rfp_value, (int, float)):
                score = numeric_match(rfp_value, sku_value)
            else:
                score = exact_match(rfp_value, sku_value)

        # Normalize None
        if score is None:
            total -= 1
            continue

        matched += score

        # --- Gap Detection ---
        if score == 1:
            gap = "Exact Match"
        elif score == 0.5:
            gap = "Partial Match"
        else:
            if sku_value is None:
                gap = "Missing in SKU"
            else:
                gap = "Mismatch"

        explanation[source_key] = {
            "mapped_to": target_key,
            "rfp_value": rfp_value,
            "sku_value": sku_value,
            "score": score,
            "gap": gap
        }

    percent = (matched / total) * 100 if total > 0 else 0

    return round(percent, 2), explanation