import os
import json

from backend.document_intelligence.ingestion.pdf_loader import load_pdf
from backend.document_intelligence.preprocessing.cleaner import clean_pages
from backend.document_intelligence.sectioning.section_detector import detect_sections
from backend.document_intelligence.chunking.chunker import chunk_sections
from backend.document_intelligence.extraction.rule_extractor import (
    extract_technical_specs,
    extract_quantities,
    extract_testing_requirements
)
from backend.document_intelligence.extraction.ner_extractor import (
    extract_entities_from_chunks
)


def parse_rfp(pdf_path: str, rfp_id: str = "RFP_001") -> dict:
    """
    Phase 6: Structured JSON Output
    Consolidates outputs from Phase 1–5 into a single schema.
    """

    # Phase 1 & 2
    pages = load_pdf(pdf_path)
    cleaned_pages = clean_pages(pages)

    # Phase 3
    sections = detect_sections(cleaned_pages)

    # Phase 4
    chunked_sections = chunk_sections(sections)

    # Phase 5
    technical_specs = extract_technical_specs(
        chunked_sections["technical_specifications"]
    )
    quantities = extract_quantities(
        chunked_sections["quantities"]
    )
    testing_requirements = extract_testing_requirements(
        chunked_sections["testing_and_acceptance"]
    )
    ner_entities = extract_entities_from_chunks(
        chunked_sections["technical_specifications"]
    )

    # Phase 6 — Structured JSON
    structured_output = {
        "rfp_id": rfp_id,

        "document_metadata": {
            "document_type": "RFP"
        },

        "scope_of_supply": {
            "description": sections["scope_of_supply"]
        },

        "technical_requirements": {
            "specifications": technical_specs,
            "ner_entities": {
                "materials": ner_entities.get("MATERIAL", []),
                "manufacturers": ner_entities.get("ORG", [])
            }
        },

        "commercial_requirements": {
            "quantities": quantities
        },

        "testing_and_acceptance": {
            "tests_required": testing_requirements
        }
    }

    return structured_output


# -------------------------------
# PHASE 6 MANUAL TEST
# -------------------------------
if __name__ == "__main__":
    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    pdf_path = os.path.join(PROJECT_ROOT, "data", "rfps", "sample_rfp.pdf")

    result = parse_rfp(pdf_path)

    print(json.dumps(result, indent=4))
