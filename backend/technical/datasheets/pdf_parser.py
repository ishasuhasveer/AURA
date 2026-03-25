import pdfplumber
import re
from backend.schemas.technical_schema import empty_sku


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from the entire PDF with progress logging.
    Safe for large industrial catalogues.
    """
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages in PDF: {total_pages}")

        for i, page in enumerate(pdf.pages, start=1):
            print(f"Processing page {i}/{total_pages}...")
            text = page.extract_text()
            if text:
                pages_text.append(text)

    return "\n".join(pages_text)

def extract_voltage(text: str):
    """
    Look for voltage patterns like:
    - 1.1 kV
    - 1100 V
    """
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*(kV|KV|V)\b", text)
    return match.group(0) if match else None


def extract_conductor(text: str):
    """
    Identify conductor material.
    """
    if re.search(r"\bcopper\b", text, re.IGNORECASE):
        return "Copper"
    if re.search(r"\baluminium\b|\baluminum\b", text, re.IGNORECASE):
        return "Aluminium"
    return None


def extract_insulation(text: str):
    """
    Identify insulation type.
    """
    if re.search(r"\bXLPE\b", text, re.IGNORECASE):
        return "XLPE"
    if re.search(r"\bPVC\b", text, re.IGNORECASE):
        return "PVC"
    return None


def extract_standard(text: str):
    """
    Identify compliance standards.
    """
    match = re.search(r"\b(IEC\s*\d+|IS\s*\d+)\b", text)
    return match.group(0) if match else None


def extract_sku_from_text(text: str, sku_id: str, source_doc: str):
    """
    Populate SKU schema using deterministic rules.
    """
    sku = empty_sku(sku_id, source_doc)

    sku["voltage"] = extract_voltage(text)
    sku["conductor"] = extract_conductor(text)
    sku["insulation"] = extract_insulation(text)
    sku["standard"] = extract_standard(text)

    # OPTIONAL FIELD
    sku["attributes"]["core_count"] = extract_core_count(text)
    sku["attributes"]["cross_section_mm2"] = extract_cross_section(text)
    sku["attributes"]["armouring"] = extract_armouring(text)

    return sku

def extract_core_count(text: str):
    """
    Extract number of cores from text.
    Examples:
    - 1 Core
    - 3 Core
    - 4C
    """
    # Pattern like "3 Core", "4 core"
    match = re.search(r"\b(\d+)\s*core\b", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Pattern like "3C", "4C"
    match = re.search(r"\b(\d+)C\b", text)
    if match:
        return int(match.group(1))

    return None

def extract_cross_section(text: str):
    """
    Extract conductor cross-section in sqmm / mm2.
    Examples:
    - 35 sqmm
    - 50 mm2
    - 70 mm²
    """
    matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(sqmm|mm2|mm²)\b",
        text,
        re.IGNORECASE
    )

    if not matches:
        return None

    # Convert all matches to float
    values = [float(match[0]) for match in matches]

    # Return smallest size (common conservative choice)
    return min(values)

def extract_armouring(text: str):
    """
    Extract armouring information.
    Priority:
    - SWA / STA
    - Armoured
    - Unarmoured
    """
    # Most specific first
    if re.search(r"\bSWA\b", text, re.IGNORECASE):
        return "SWA"

    if re.search(r"\bSTA\b", text, re.IGNORECASE):
        return "STA"

    # Explicit unarmoured
    if re.search(r"\bunarmoured\b|\bunarmored\b", text, re.IGNORECASE):
        return "Unarmoured"

    # Generic armoured
    if re.search(r"\barmoured\b|\barmored\b", text, re.IGNORECASE):
        return "Armoured"

    return None


if __name__ == "__main__":

    pdf_path = "data/datasheets/sample_cable.pdf"

    text = extract_text_from_pdf(pdf_path)

    sku = extract_sku_from_text(
        text,
        sku_id="SKU_SAMPLE",
        source_doc=pdf_path
    )

    print("\n--- EXTRACTED SKU ---\n")
    print(sku)
