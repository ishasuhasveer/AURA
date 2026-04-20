# =========================
# SPEC MAPPING CONFIG
# =========================

SPEC_MAPPING = {
    "voltage_kv": {
        "target": "voltage_kv",
        "type": "numeric"
    },
    "insulation_type": {
        "target": "insulation_type",
        "type": "categorical"
    },
    "flame_type": {  # 🔥 NEW
        "target": "flame_type",
        "type": "categorical"
    },
    "standard": {
        "target": "standard",
        "type": "exact"
    },
    "cores": {
        "target": "cores",
        "type": "numeric"
    },
    "conductor": {
        "target": "conductor",
        "type": "categorical"
    },
    "current_air": {  # 🔥 FIXED (was current_rating)
        "target": "current_air",
        "type": "numeric"
    },
    "cross_section_mm2": {
        "target": "cross_section_mm2",
        "type": "numeric"
    }
}

# =========================
# HARD CONSTRAINTS
# =========================

HARD_CONSTRAINTS = {
    "cross_section_mm2",
    "voltage_kv",
    "cores",
    "conductor"
}


# =========================
# NORMALIZATION HELPERS
# =========================

def normalize_value(key, value):
    if value is None:
        return None

    val = str(value).strip()

    # ----------------------
    # Voltage
    # ----------------------
    if key == "voltage_kv":
        try:
            v = float(val)
            if v <= 0 or v > 1000:  # 🔥 FIXED RANGE
                return None
            return v
        except:
            return None

    # ----------------------
    # Cross Section
    # ----------------------
    if key == "cross_section_mm2":
        try:
            v = float(val)
            if v < 1 or v > 3000:
                return None
            return v
        except:
            return None

    # ----------------------
    # Insulation
    # ----------------------
    if key == "insulation_type":
        val = val.upper()

        if "XLPE" in val:
            return "XLPE"
        if "PVC" in val:
            return "PVC"

        return None

    # ----------------------
    # Flame Type (NEW)
    # ----------------------
    if key == "flame_type":
        val = val.upper()

        if "FRLS" in val:
            return "FRLS"
        if "FR" in val:
            return "FR"

        return "NORMAL"

    # ----------------------
    # Cores
    # ----------------------
    if key == "cores":
        try:
            v = int(val)
            if v <= 0 or v > 10:
                return None
            return v
        except:
            return None

    # ----------------------
    # Conductor
    # ----------------------
    if key == "conductor":
        val = val.lower()

        if "/" in val:
            return "copper"

        if "copper" in val or "cu" in val:
            return "copper"

        if "aluminium" in val or "aluminum" in val or "al" in val:
            return "aluminium"

        return None

    # ----------------------
    # Current
    # ----------------------
    if key == "current_air":
        try:
            v = float(val)
            if v < 10 or v > 2000:
                return None
            return v
        except:
            return None

    # ----------------------
    # Standard
    # ----------------------
    if key == "standard":
        import re
        match = re.search(r'(IS\s*\d{3,5}|IEC\s*\d{3,5}|BS\s*\d{3,5})', val, re.IGNORECASE)

        if match:
            return match.group(1).replace(" ", "").upper()

        return None

    return val


# =========================
# MAIN MAPPING FUNCTION
# =========================

def map_rfp_to_product(rfp_specs):
    mapped = {}

    for rfp_key, raw_value in rfp_specs.items():

        if rfp_key not in SPEC_MAPPING:
            continue

        mapping = SPEC_MAPPING[rfp_key]

        normalized_value = normalize_value(rfp_key, raw_value)

        if normalized_value is None:
            continue

        mapped[mapping["target"]] = {
            "value": normalized_value,
            "type": mapping["type"],
            "source": rfp_key,
            "hard": mapping["target"] in HARD_CONSTRAINTS
        }

    return mapped