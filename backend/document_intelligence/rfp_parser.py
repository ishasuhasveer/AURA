import re
from typing import Dict, Any


def parse_rfp(text: str, rfp_id: str = "RFP_001") -> Dict[str, Any]:
    """
    Simplified RFP parser.

    Converts extracted RFP text → structured JSON
    aligned with downstream agents (Technical + Pricing).
    """

    text_lower = text.lower()

    # ----------------------------
    # TECHNICAL REQUIREMENTS
    # ----------------------------
    voltage = None
    if "11kv" in text_lower:
        voltage = "11kV"
    elif "33kv" in text_lower:
        voltage = "33kV"

    conductor = None
    if "copper" in text_lower:
        conductor = "copper"
    elif "aluminium" in text_lower:
        conductor = "aluminium"

    standard = None
    if "iec" in text_lower:
        standard = "IEC"
    elif "is" in text_lower:
        standard = "IS"

    technical_requirements = {
        "voltage": voltage,
        "conductor": conductor,
        "standard": standard
    }

    # ----------------------------
    # QUANTITIES
    # ----------------------------
    quantities = {
        "estimated_quantity": None
    }

    numbers = re.findall(r"\d+", text)
    if numbers:
        quantities["estimated_quantity"] = int(numbers[0])

    # ----------------------------
    # TESTING REQUIREMENTS
    # ----------------------------
    testing_requirements = []

    if "test" in text_lower:
        testing_requirements.append("standard testing required")

    # ----------------------------
    # FINAL OUTPUT
    # ----------------------------
    structured_output = {
        "rfp_id": rfp_id,

        "technical_requirements": technical_requirements,

        "quantities": quantities,

        "testing_requirements": testing_requirements
    }

    return structured_output


# -------------------------------
# MANUAL TEST
# -------------------------------
if __name__ == "__main__":

    sample_text = """
    RFP for electrical cable supply.
    Deadline: 15 February 2026
    Voltage: 11kV
    Conductor: Copper
    Standard: IEC
    Quantity: 100 units
    """

    result = parse_rfp(sample_text)

    import json
    print(json.dumps(result, indent=4))