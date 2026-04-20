import re
from typing import List


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


# --------------------------------------------------
# SAFE NUMBER EXTRACTION
# --------------------------------------------------

def extract_numbers(text: str):
    nums = re.findall(r"\d+\.?\d*", text)
    values = []

    for n in nums:
        try:
            val = float(n)
            if val < 0.1 or val > 5000:
                continue
            values.append(val)
        except:
            continue

    return values


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize_insulation(text: str):
    text = text.upper()

    if "PVC" in text:
        return "PVC"
    if "XLPE" in text:
        return "XLPE"

    return None


def normalize_flame_type(text: str):
    text = text.upper()

    if "FRLS" in text:
        return "FRLS"
    if "FR" in text:
        return "FR"

    return "NORMAL"


def normalize_voltage(text: str):
    matches = re.findall(r'(\d+\.?\d*)\s*kV', text, re.IGNORECASE)

    values = []
    for m in matches:
        try:
            val = float(m)
            if 0.1 <= val <= 1000:
                values.append(val)
        except:
            continue

    return max(values) if values else None


def normalize_standard(text: str):
    match = re.search(r'(IS[-\s]?\d{3,5}|IEC[-\s]?\d{3,5}|BS[-\s]?\d{3,5})', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "").upper()
    return None


def normalize_cores(text: str):
    matches = re.findall(r'(\d+)\s*(core|c)', text, re.IGNORECASE)
    values = [int(m[0]) for m in matches if int(m[0]) <= 10]
    return max(values) if values else None


def normalize_conductor(text: str):
    text = text.lower()

    if "copper" in text or "cu" in text:
        return "copper"

    if "aluminium" in text or "aluminum" in text or "al" in text:
        return "aluminium"

    return None


def normalize_cross_section(text: str):

    matches = re.findall(
        r'(\d+(\.\d+)?)\s*(sq\.?\s*mm|mm2|sqmm|sq\.mm)',
        text,
        re.IGNORECASE
    )

    values = [float(m[0]) for m in matches if 1 <= float(m[0]) <= 5000]

    return max(values) if values else None


def normalize_current(text: str):
    matches = re.findall(r'(\d+)\s*A', text, re.IGNORECASE)

    values = []
    for m in matches:
        val = int(m)
        if 10 <= val <= 2000:
            values.append(val)

    return max(values) if values else None


# --------------------------------------------------
# CORE EXTRACTION
# --------------------------------------------------

def extract_structured_requirements(chunks: List[str]) -> List[dict]:

    result = []

    combined_text = clean_text(" ".join(chunks))

    voltage = normalize_voltage(combined_text)
    insulation = normalize_insulation(combined_text)
    flame_type = normalize_flame_type(combined_text)
    standard = normalize_standard(combined_text)
    cores = normalize_cores(combined_text)
    conductor = normalize_conductor(combined_text)
    current = normalize_current(combined_text)

    # 🔥 SIZE EXTRACTION (chunk-wise priority)
    cross_section = None
    for chunk in chunks:
        val = normalize_cross_section(chunk)
        if val:
            cross_section = val
            break

    # ---------------- BUILD RESULT ----------------

    if cross_section:
        result.append({"parameter": "cross_section_mm2", "value": cross_section})

    if voltage:
        result.append({"parameter": "voltage_kv", "value": voltage})

    if insulation:
        result.append({"parameter": "insulation_type", "value": insulation})

    if flame_type:
        result.append({"parameter": "flame_type", "value": flame_type})

    if standard:
        result.append({"parameter": "standard", "value": standard})

    if cores:
        result.append({"parameter": "cores", "value": cores})

    if conductor:
        result.append({"parameter": "conductor", "value": conductor})

    if current:
        result.append({"parameter": "current_air", "value": current})

    return result


# --------------------------------------------------
# QUANTITY EXTRACTION (FIXED)
# --------------------------------------------------

def extract_quantities(chunks: List[str]) -> dict:

    quantity = None
    unit = None

    for chunk in chunks:

        # meters
        m = re.search(r'(\d+)\s*(mtr|meter|meters|m)', chunk, re.IGNORECASE)
        if m:
            quantity = float(m.group(1))
            unit = "meter"
            break

        # km → convert
        km = re.search(r'(\d+)\s*(km)', chunk, re.IGNORECASE)
        if km:
            quantity = float(km.group(1)) * 1000
            unit = "meter"
            break

        # units
        u = re.search(r'(\d+)\s*(nos|units|qty)', chunk, re.IGNORECASE)
        if u:
            quantity = float(u.group(1))
            unit = "unit"
            break

    if not quantity:
        return {}

    return {
        "estimated_quantity": quantity,
        "unit": unit
    }


# --------------------------------------------------
# TESTING EXTRACTION
# --------------------------------------------------

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