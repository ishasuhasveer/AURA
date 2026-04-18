import re
from typing import List


# -------------------------------
# NORMALIZATION FUNCTIONS
# -------------------------------

def normalize_insulation(text: str) -> str:
    text = text.upper()

    for key in ["FRLS", "XLPE", "PVC", "HDPE"]:
        if key in text:
            return key

    return None


def normalize_voltage(text: str):
    # kV
    match_kv = re.search(r'(\d+\.?\d*)\s*kV', text, re.IGNORECASE)
    if match_kv:
        return float(match_kv.group(1))

    # V (convert to kV)
    match_v = re.search(r'(\d+)\s*V', text, re.IGNORECASE)
    if match_v:
        return round(int(match_v.group(1)) / 1000, 2)

    return None


def normalize_standard(text: str) -> str:
    match = re.search(r'(IS[-\s]?\d+|IEC[-\s]?\d+|BS[-\s]?\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "").upper()
    return None


def normalize_cores(text: str):
    match = re.search(r'(\d+)\s*core', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def normalize_conductor(text: str):
    match = re.search(r'(\d+/\d+\.?\d*)\s*mm', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def normalize_cross_section(text: str):
    match = re.search(r'(\d+(\.\d+)?)\s*(sq\.?mm|mm2)', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def normalize_current(text: str):
    match = re.search(r'(\d+)\s*A', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


# -------------------------------
# CORE EXTRACTION
# -------------------------------

def extract_structured_requirements(chunks: List[str]) -> List[dict]:

    result = []
    combined_text = " ".join(chunks)

    voltage = normalize_voltage(combined_text)
    insulation = normalize_insulation(combined_text)
    standard = normalize_standard(combined_text)
    cores = normalize_cores(combined_text)
    conductor = normalize_conductor(combined_text)
    cross_section = normalize_cross_section(combined_text)
    current = normalize_current(combined_text)

    # ---------------- CABLE SPECS ----------------
    if voltage:
        result.append({"parameter": "voltage_kv", "value": voltage})

    if insulation:
        result.append({"parameter": "insulation_type", "value": insulation})

    if standard:
        result.append({"parameter": "standard", "value": standard})

    if cores:
        result.append({"parameter": "cores", "value": cores})

    if conductor:
        result.append({"parameter": "conductor", "value": conductor})

    if cross_section:
        result.append({"parameter": "cross_section_mm2", "value": cross_section})

    # ---------------- ELECTRICAL FITTINGS ----------------
    if current:
        result.append({"parameter": "current_rating", "value": current})

    # Detect type (basic)
    text_lower = combined_text.lower()

    if "switch" in text_lower:
        result.append({"parameter": "fitting_type", "value": "switch"})

    elif "socket" in text_lower:
        result.append({"parameter": "fitting_type", "value": "socket"})

    elif "mcb" in text_lower:
        result.append({"parameter": "fitting_type", "value": "mcb"})

    return result


# -------------------------------
# QUANTITY EXTRACTION
# -------------------------------

def extract_quantities(chunks: List[str]) -> dict:
    quantity = None

    for chunk in chunks:
        match = re.search(r'(\d+)\s*(km|KM|mtr|meters|nos|units)', chunk)
        if match:
            quantity = int(match.group(1))
            break

    return {
        "estimated_quantity": quantity
    }


# -------------------------------
# TESTING EXTRACTION
# -------------------------------

def extract_testing_requirements(chunks: List[str]) -> List[str]:
    tests = set()

    for chunk in chunks:
        chunk_lower = chunk.lower()

        if "high voltage" in chunk_lower:
            tests.add("high_voltage_test")

        if "pre-delivery" in chunk_lower:
            tests.add("pre_delivery_inspection")

        if "acceptance" in chunk_lower:
            tests.add("acceptance_test")

    return sorted(list(tests))