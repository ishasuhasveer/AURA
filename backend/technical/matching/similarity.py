def exact_match(rfp_value, sku_value):
    """
    Exact + partial match comparator for categorical specs.
    """

    if rfp_value is None:
        return None

    if sku_value is None:
        return 0.0

    rfp_norm = str(rfp_value).strip().upper()
    sku_norm = str(sku_value).strip().upper()

    # Exact match
    if rfp_norm == sku_norm:
        return 1.0

    # Partial match (substring)
    if rfp_norm in sku_norm or sku_norm in rfp_norm:
        return 0.5

    return 0.0


def numeric_match(rfp_value, sku_value, tolerance=0.05):
    """
    Numeric match with tolerance and safe parsing.
    """

    if rfp_value is None:
        return None

    if sku_value is None:
        return 0.0

    try:
        rfp_val = float(str(rfp_value).replace(" ", "").replace("mm2", "").replace("sq", ""))
        sku_val = float(str(sku_value).replace(" ", "").replace("mm2", "").replace("sq", ""))
    except Exception:
        return 0.0  # fallback safe

    # Within tolerance → exact
    if abs(sku_val - rfp_val) / (rfp_val + 1e-10) <= tolerance:
        return 1.0

    # Over-spec
    if sku_val > rfp_val:
        return 0.5

    return 0.0