import re
import os
from typing import List, Dict


def detect_sections(pages: List[Dict]) -> Dict[str, str]:
    """
    Detects and extracts key RFP sections:
    - Scope of Supply
    - Technical Specifications
    - Quantities
    - Testing & Acceptance
    """

    full_text = "\n".join([p["text"] for p in pages])

    sections = {
        "scope_of_supply": "",
        "technical_specifications": "",
        "quantities": "",
        "testing_and_acceptance": ""
    }

    # -------- TECHNICAL SPECIFICATIONS --------
    tech_match = re.search(
        r"2\.\s*SPECIFICATIONS OF COPPER CABLES:(.*?)(Part-II|Price Bid format)",
        full_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    if tech_match:
        sections["technical_specifications"] = tech_match.group(1).strip()

    # -------- TESTING & ACCEPTANCE --------
    test_matches = re.findall(
        r"(Acceptance Test Plan.*?|High voltage test.*?|Pre-delivery inspection.*?)\n",
        full_text,
        flags=re.IGNORECASE
    )
    sections["testing_and_acceptance"] = "\n".join(test_matches).strip()

    # -------- QUANTITIES --------
    quantity_matches = re.findall(
        r"Quantity\s+([\d\.]+\s*(Km|mtr|meters).*?)\n",
        full_text,
        flags=re.IGNORECASE
    )
    sections["quantities"] = "\n".join([" ".join(q) for q in quantity_matches])

    # -------- SCOPE OF SUPPLY --------
    scope_match = re.search(
        r"SUPPLY OF .*?CABLES.*?(?=1\.1\.|2\.)",
        full_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    if scope_match:
        sections["scope_of_supply"] = scope_match.group(0).strip()

    return sections


# -------------------------------
# PHASE 3 MANUAL TEST
# -------------------------------
if __name__ == "__main__":
    from backend.document_intelligence.ingestion.pdf_loader import load_pdf
    from backend.document_intelligence.preprocessing.cleaner import clean_pages

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    pdf_path = os.path.join(PROJECT_ROOT, "data", "rfps","sample_rfp.pdf")

    pages = load_pdf(pdf_path)
    cleaned_pages = clean_pages(pages)

    extracted_sections = detect_sections(cleaned_pages)

    print("\n====== DETECTED SECTIONS ======\n")
    for key, value in extracted_sections.items():
        print(f"\n--- {key.upper()} ---\n")
        print(value[:800] if value else "NOT FOUND")
