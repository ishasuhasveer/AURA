from typing import Dict, Any

from backend.document_intelligence.ingestion.pdf_loader import load_pdf
from backend.document_intelligence.preprocessing.cleaner import clean_pages
from backend.document_intelligence.sectioning.section_detector import detect_sections

from backend.document_intelligence.extraction.rule_extractor import (
    extract_structured_requirements,
    extract_quantities,
    extract_testing_requirements
)


def generate_summary(sections: Dict[str, str]) -> Dict:
    scope_text = sections.get("scope_of_supply", "")

    return {
        "scope": scope_text[:200] if scope_text else None,
        "category": "cable_supply"
    }


def parse_rfp(file_path: str, rfp_id: str = "RFP_001") -> Dict[str, Any]:
    """
    FULL PIPELINE: file_path → structured JSON
    """

    # ✅ Step 1: Load PDF
    pages = load_pdf(file_path)

    # ✅ Step 2: Clean
    cleaned = clean_pages(pages)

    # ✅ Step 3: Section detection
    sections = detect_sections(cleaned)

    # ✅ Step 4: Extract
    tech_chunks = [sections.get("technical_specifications", "")]
    qty_chunks = [sections.get("quantities", "")]
    test_chunks = [sections.get("testing_and_acceptance", "")]

    structured_output = {
        "rfp_id": rfp_id,

        "summary": generate_summary(sections),

        "key_requirements": extract_structured_requirements(tech_chunks) or [],
        "quantities": extract_quantities(qty_chunks) or {},
        "testing_requirements": extract_testing_requirements(test_chunks) or []
    }

    return structured_output