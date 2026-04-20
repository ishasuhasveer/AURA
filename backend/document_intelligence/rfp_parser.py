from typing import Dict, Any

from backend.document_intelligence.ingestion.pdf_loader import load_pdf
from backend.document_intelligence.preprocessing.cleaner import clean_pages
from backend.document_intelligence.sectioning.section_detector import detect_sections
from backend.document_intelligence.extraction.ner_extractor import extract_entities

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
# CONVERT LIST → DICT
# --------------------------------------------------

def convert_to_spec_dict(requirements_list):
    spec_dict = {}

    for item in requirements_list:
        if not isinstance(item, dict):
            continue

        param = item.get("parameter")
        value = item.get("value")

        if not param:
            continue

        # 🔥 DO NOT overwrite good values
        if param not in spec_dict:
            spec_dict[param] = value

    return spec_dict


# --------------------------------------------------
# MAIN PARSER (ROBUST)
# --------------------------------------------------

# --------------------------------------------------
# 🔥 VALUE CLEANING
# --------------------------------------------------
import re

def clean_value(val, key=None):
    if val is None:
        return None

    if isinstance(val, str):
        val = val.replace("\n", " ").strip()

        # 🔥 DO NOT TOUCH STANDARD
        if key == "standard":
            return val.replace(" ", "").upper()

        # Numeric only for specific fields
        if key in ["voltage_kv", "current_rating", "cross_section_mm2", "cores"]:
            import re
            nums = re.findall(r"\d+\.?\d*", val)
            if nums:
                return float(nums[0])
            return None

        return val

    return val


# --------------------------------------------------
# 🔥 SPEC VALIDATION (CRITICAL FIX)
# --------------------------------------------------

def validate_specs(specs: dict) -> dict:
    clean_specs = {}

    for k, v in specs.items():

        v = clean_value(v, k)

        if v is None:
            continue

        # ---------------- DOMAIN RULES ----------------

        if k == "voltage_kv":
            if isinstance(v, (int, float)) and (v <= 0 or v > 1000):
                continue

        if k == "cores":
            if isinstance(v, (int, float)) and (v <= 0 or v > 10):
                continue

        if k == "current_rating":
            if isinstance(v, (int, float)) and (v <= 0 or v > 5000):
                continue

        if k == "cross_section_mm2":
            if isinstance(v, (int, float)) and (v <= 0 or v > 3000):
                continue

        # Clean standard
        if k == "standard" and isinstance(v, str):
            v = v.replace(" ", "").upper()

        clean_specs[k] = v

    return clean_specs


def prioritize_specs(specs: dict) -> dict:
    """
    Keep only high-value engineering parameters.
    Avoid noise like weak current or bad standards.
    """

    PRIORITY_KEYS = [
        "cross_section_mm2",
        "voltage_kv",
        "insulation_type",
        "cores",
        "conductor"
    ]

    prioritized = {}

    for key in PRIORITY_KEYS:
        if key in specs:
            prioritized[key] = specs[key]

    return prioritized



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

    tech_text = sections.get("technical_specifications")
    if not tech_text:
        tech_text = full_text

    qty_text = sections.get("quantities") or full_text
    test_text = sections.get("testing_and_acceptance") or full_text

    # 🔥 split into meaningful chunks (line-level)
    chunks = [c.strip() for c in tech_text.split("\n") if len(c.strip()) > 5]
    raw_requirements = extract_structured_requirements(chunks) or []

    raw_quantities = extract_quantities([qty_text]) or {}

    # 🔥 Normalize quantity (meter-based default)
    normalized_quantities = {}

    for k, v in raw_quantities.items():
        try:
            val = float(v)
            if val > 0:
                normalized_quantities[k] = val
        except:
            continue

    # fallback: if nothing extracted, assume 1
    if not normalized_quantities:
        normalized_quantities["default"] = 1

    # Convert raw → dict
    technical_requirements = convert_to_spec_dict(raw_requirements)

    # 🔥 CLEAN + VALIDATE
    technical_requirements = validate_specs(technical_requirements)

    # 🔥 SOFT PRIORITIZATION
    priority_order = [
        "cross_section_mm2",
        "voltage_kv",
        "insulation_type",
        "cores",
        "conductor"
    ]

    technical_requirements = {
        **{k: technical_requirements[k] for k in priority_order if k in technical_requirements},
        **technical_requirements
    }

    # 🔥 NER ENRICHMENT (NEW)
    ner_output = extract_entities(full_text)
    structured_ner = ner_output.get("structured", {})

    # Merge only missing fields
    for k, v in structured_ner.items():
        if k not in technical_requirements:
            technical_requirements[k] = v

    # 🔥 ONLY fallback if NOTHING meaningful found
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
    print("CLEANED REQUIREMENTS:", technical_requirements)
    print("CATEGORY:", summary["category"])
    print("====== END DEBUG ======\n")

    print("🔥 FINAL TECH SPECS SENT TO TECH AGENT:", technical_requirements)

    # ---------------- FINAL OUTPUT ----------------
    return {
        "rfp_id": rfp_id,
        "summary": summary,
        "technical_requirements": technical_requirements,
        "quantities": normalized_quantities,
        "testing_requirements": extract_testing_requirements([test_text]) or []
    }