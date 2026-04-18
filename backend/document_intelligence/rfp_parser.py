from typing import Dict, Any

from backend.document_intelligence.ingestion.pdf_loader import load_pdf
from backend.document_intelligence.preprocessing.cleaner import clean_pages
from backend.document_intelligence.sectioning.section_detector import detect_sections

from backend.document_intelligence.extraction.rule_extractor import (
    extract_structured_requirements,
    extract_quantities,
    extract_testing_requirements
)


# --------------------------------------------------
# 🔥 SEMANTIC FALLBACK (CRITICAL)
# --------------------------------------------------

def extract_semantic_fallback(text: str) -> dict:
    text_lower = text.lower()
    fallback = {}

    # ---------------- PRODUCT DETECTION ----------------
    if "cable" in text_lower or "wire" in text_lower:
        fallback["product_type"] = "cable"

    elif "switch" in text_lower or "socket" in text_lower or "fitting" in text_lower:
        fallback["product_type"] = "electrical_fittings"

    elif "mcb" in text_lower or "distribution board" in text_lower or "db" in text_lower:
        fallback["product_type"] = "electrical_fittings"

    elif "diesel tank" in text_lower:
        fallback["product_type"] = "diesel_tank"

    elif "transformer" in text_lower:
        fallback["product_type"] = "transformer"

    elif "panel" in text_lower:
        fallback["product_type"] = "electrical_panel"

    # ---------------- APPLICATION ----------------
    if "generator" in text_lower:
        fallback["application"] = "generator"

    # ---------------- DURATION ----------------
    import re
    duration = re.search(r'(\d+)\s*hours?', text_lower)
    if duration:
        fallback["backup_duration_hours"] = int(duration.group(1))

    return fallback

# --------------------------------------------------
# 🔥 CATEGORY DETECTION
# --------------------------------------------------

def detect_category_from_text(text: str) -> str:
    text_lower = text.lower()

    # 🔥 HIGH PRIORITY (DOMAIN CONTROL)
    if "cable" in text_lower:
        return "cable_supply"

    if "wire" in text_lower:
        return "cable_supply"

    if "electrical panel" in text_lower:
        return "electrical_fittings"

    if "transformer" in text_lower:
        return "transformer_supply"

    if "diesel tank" in text_lower:
        return "fuel_storage"

    return "general_supply"

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def generate_summary(sections: Dict[str, str], full_text: str, tech_data: dict) -> Dict:

    scope_text = sections.get("scope_of_supply") or full_text[:300]

    return {
        "scope": scope_text[:300] if scope_text else None,
        "category": detect_category(tech_data)
    }


# --------------------------------------------------
# CONVERT LIST → DICT
# --------------------------------------------------

def convert_to_spec_dict(requirements_list):
    spec_dict = {}

    for item in requirements_list:
        if isinstance(item, dict):
            param = item.get("parameter")
            value = item.get("value")

            if param:
                spec_dict[param] = value

    return spec_dict


# --------------------------------------------------
# MAIN PARSER (ROBUST)
# --------------------------------------------------

def parse_rfp(file_path: str, rfp_id: str = "RFP_001") -> Dict[str, Any]:

    # ---------------- LOAD ----------------
    pages = load_pdf(file_path)
    cleaned = clean_pages(pages)
    sections = detect_sections(cleaned)

    # 🔥 Combine ALL text (CRITICAL FIX)
    full_text = " ".join(
        page["text"] if isinstance(page, dict) else str(page)
        for page in cleaned
    )

    # ---------------- EXTRACTION ----------------

    # Prefer section → fallback to full text
    tech_text = sections.get("technical_specifications") or full_text

    qty_text = sections.get("quantities") or full_text
    test_text = sections.get("testing_and_acceptance") or full_text

    # ---------------- STRUCTURED EXTRACTION ----------------
    raw_requirements = extract_structured_requirements([tech_text]) or []

    technical_requirements = convert_to_spec_dict(raw_requirements)

    # ---------------- 🔥 FALLBACK IF EMPTY ----------------
    if not technical_requirements:
        print("⚠️ Structured extraction failed → using semantic fallback")

        fallback_data = extract_semantic_fallback(full_text)

        technical_requirements = fallback_data

    # ---------------- SUMMARY ----------------
    def generate_summary(sections: Dict[str, str], full_text: str) -> Dict:
        scope_text = sections.get("scope_of_supply") or full_text[:300]

        category = detect_category_from_text(full_text)

        return {
            "scope": scope_text[:300] if scope_text else None,
            "category": category
        }

    summary = generate_summary(sections, full_text)
    # ---------------- DEBUG ----------------
    print("\n====== RFP PARSER DEBUG ======")
    print("RAW REQUIREMENTS:", raw_requirements)
    print("FINAL TECH REQ:", technical_requirements)
    print("CATEGORY:", summary["category"])
    print("====== END DEBUG ======\n")

    # ---------------- FINAL OUTPUT ----------------
    return {
        "rfp_id": rfp_id,
        "summary": summary,
        "technical_requirements": technical_requirements,
        "quantities": extract_quantities([qty_text]) or {},
        "testing_requirements": extract_testing_requirements([test_text]) or []
    }