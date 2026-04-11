from typing import Dict, Any
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


def parse_rfp(sections: Dict[str, str], rfp_id: str = "RFP_001") -> Dict[str, Any]:
    """
    FINAL STRUCTURED OUTPUT (STRICT SCHEMA)
    """

    tech_chunks = [sections.get("technical_specifications", "")]
    qty_chunks = [sections.get("quantities", "")]
    test_chunks = [sections.get("testing_and_acceptance", "")]

    structured_output = {
        "rfp_id": rfp_id,

        "summary": generate_summary(sections),

        "key_requirements": extract_structured_requirements(tech_chunks),

        "quantities": extract_quantities(qty_chunks),

        "testing_requirements": extract_testing_requirements(test_chunks)
    }

    return structured_output


# ---------------- TEST ----------------
if __name__ == "__main__":
    from backend.document_intelligence.ingestion.pdf_loader import load_pdf
    from backend.document_intelligence.preprocessing.cleaner import clean_pages
    from backend.document_intelligence.sectioning.section_detector import detect_sections
    import os, json

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    pdf_path = os.path.join(PROJECT_ROOT, "data", "rfps", "sample_rfp.pdf")

    pages = load_pdf(pdf_path)
    cleaned = clean_pages(pages)
    sections = detect_sections(cleaned)

    result = parse_rfp(sections)

    print(json.dumps(result, indent=4))