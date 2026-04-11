import re
from typing import Dict, List


# -------------------------------
# NORMALIZATION FUNCTIONS
# -------------------------------

def normalize_insulation(text: str) -> str:
    text = text.upper()

    if "FRLS" in text:
        return "FRLS"
    if "XLPE" in text:
        return "XLPE"
    if "PVC" in text:
        return "PVC"
    if "HDPE" in text:
        return "HDPE"

    return None


def normalize_voltage(text: str) -> int:
    match = re.search(r'(\d+\.?\d*)\s*kV', text, re.IGNORECASE)
    if match:
        return int(float(match.group(1)))
    return None


def normalize_standard(text: str) -> str:
    match = re.search(r'(IS[-\s]?\d+|IEC[-\s]?\d+|BS[-\s]?\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "").upper()
    return None


# -------------------------------
# CORE EXTRACTION (STRUCTURED ONLY)
# -------------------------------

def extract_structured_requirements(chunks: List[str]) -> Dict:
    """
    Converts raw chunks → structured schema (STRICT FORMAT)
    """

    result = {
        "voltage_kv": None,
        "insulation_type": None,
        "standard": None
    }

    for chunk in chunks:

        if not result["voltage_kv"]:
            result["voltage_kv"] = normalize_voltage(chunk)

        if not result["insulation_type"]:
            result["insulation_type"] = normalize_insulation(chunk)

        if not result["standard"]:
            result["standard"] = normalize_standard(chunk)

    return result


# -------------------------------
# QUANTITY EXTRACTION
# -------------------------------

def extract_quantities(chunks: List[str]) -> Dict:
    quantity = None

    for chunk in chunks:
        match = re.search(r'(\d+)\s*(km|KM|mtr|meters)', chunk)
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


# -------------------------------
# TEST BLOCK (IMPORTANT)
# -------------------------------
if __name__ == "__main__":

    sample_chunks = [
        "25 core copper cable with HDPE insulation rated for 3 KV as per IS 8130 standard",
        "Pre-delivery inspection and high voltage test required",
        "Quantity: 11 Km"
    ]

    tech = extract_structured_requirements(sample_chunks)
    qty = extract_quantities(sample_chunks)
    tests = extract_testing_requirements(sample_chunks)

    import json

    print("\n=== STRUCTURED OUTPUT ===\n")
    print(json.dumps({
        "key_requirements": tech,
        "quantities": qty,
        "testing_requirements": tests
    }, indent=4))