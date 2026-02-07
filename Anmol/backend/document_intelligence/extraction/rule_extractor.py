import re
from typing import Dict, List


def extract_technical_specs(chunks: List[str]) -> Dict[str, List[str]]:
    """
    Extract atomic technical specifications from technical chunks.
    """

    specs = {
        "number_of_cores": set(),
        "core_dimensions": set(),
        "insulation": set(),
        "sheathing": set(),
        "standards": set(),
        "voltage": set()
    }

    for chunk in chunks:
        specs["number_of_cores"].update(
            re.findall(r'(\d+)\s*CORE', chunk, flags=re.IGNORECASE)
        )

        specs["core_dimensions"].update(
            re.findall(r'\d+\s*/\s*\d+\.?\d*\s*mm', chunk, flags=re.IGNORECASE)
        )

        specs["insulation"].update(
            re.findall(r'(HDPE|PVC|XLPE)', chunk, flags=re.IGNORECASE)
        )

        specs["sheathing"].update(
            re.findall(r'(PVC\s*ST-\d)', chunk, flags=re.IGNORECASE)
        )

        specs["standards"].update(
            re.findall(r'(IS\s*\d+|IEC\s*\d+|BS\s*\d+)', chunk, flags=re.IGNORECASE)
        )

        specs["voltage"].update(
            re.findall(r'\d+\.?\d*\s*kV', chunk, flags=re.IGNORECASE)
        )

    return {k: sorted(list(v)) for k, v in specs.items()}


def extract_quantities(chunks: List[str]) -> List[str]:
    quantities = set()

    for chunk in chunks:
        quantities.update(
            re.findall(r'\d+\s*(Km|KM|km|mtr|meters)', chunk)
        )

    return sorted(list(quantities))


def extract_testing_requirements(chunks: List[str]) -> List[str]:
    tests = set()

    for chunk in chunks:
        tests.update(
            re.findall(
                r'(Acceptance Test Plan|High voltage test|Pre-delivery inspection)',
                chunk,
                flags=re.IGNORECASE
            )
        )

    return sorted(list(tests))
