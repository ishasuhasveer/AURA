def exact_match(rfp_value, sku_value):
    """
    Exact match comparator for categorical specs.

    Used for:
    - voltage
    - conductor
    - insulation
    - standard
    - armouring

    Returns:
    - 1.0 → exact match
    - 0.0 → mismatch or missing SKU value
    - None → RFP did not specify this field (do not evaluate)
    """

    # RFP did not ask for this spec → ignore
    if rfp_value is None:
        return None

    # SKU does not have this spec → non-compliant
    if sku_value is None:
        return 0.0

    # Normalize before comparison
    rfp_norm = str(rfp_value).strip().upper()
    sku_norm = str(sku_value).strip().upper()

    return 1.0 if rfp_norm == sku_norm else 0.0

def numeric_match(rfp_value, sku_value):
    """
    Numeric match comparator for quantitative specs.

    Used for:
    - cross_section_mm2
    - core_count (if ever used)

    Rules:
    - SKU == RFP → 1.0
    - SKU > RFP  → 0.5 (acceptable over-capacity)
    - SKU < RFP  → 0.0 (non-compliant)
    """

    # RFP did not specify → ignore
    if rfp_value is None:
        return None

    # SKU missing value → non-compliant
    if sku_value is None:
        return 0.0

    rfp_val = float(rfp_value)
    sku_val = float(sku_value)

    if sku_val == rfp_val:
        return 1.0

    if sku_val > rfp_val:
        return 0.5

    return 0.0
