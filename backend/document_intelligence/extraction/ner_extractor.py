import spacy
import re
from typing import Dict

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# CLEANING
# --------------------------------------------------

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# EXTRACTION HELPERS
# --------------------------------------------------

def extract_numbers(text: str):
    nums = re.findall(r"\d+\.?\d*", text)

    cleaned = []
    for n in nums:
        try:
            val = float(n)
            if val > 10000:
                continue
            cleaned.append(val)
        except:
            continue

    return cleaned


def extract_standard(text: str):
    match = re.search(r"(IS\s*\d+)", text, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "").upper()
    return None


def extract_voltage(text: str):
    match = re.search(r"(\d+\.?\d*)\s*(KV|kV)", text)
    if match:
        return float(match.group(1))
    return None


def extract_cross_section(text: str):
    match = re.search(r"(\d+)\s*(sq\.?\s*mm|mm2)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_cores(text: str):
    match = re.search(r"(\d+)\s*(core|c)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_conductor(text: str):
    text = text.lower()

    if "copper" in text or "cu" in text:
        return "copper"
    if "aluminium" in text or "aluminum" in text or "al" in text:
        return "aluminium"

    return None


def extract_insulation(text: str):
    text = text.upper()

    if "XLPE" in text:
        return "XLPE"
    if "PVC" in text:
        return "PVC"

    return None


def extract_flame_type(text: str):
    text = text.upper()

    if "FRLS" in text:
        return "FRLS"
    if "FR" in text:
        return "FR"

    return "NORMAL"


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def extract_entities(text: str) -> Dict:

    text = clean_text(text)
    doc = nlp(text)

    entities = {
        "organizations": set(),
        "standards": set()
    }

    # ---------------- spaCy ----------------
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organizations"].add(ent.text.strip())

    # ---------------- STRUCTURED EXTRACTION ----------------

    structured = {
        "cross_section_mm2": extract_cross_section(text),
        "voltage_kv": extract_voltage(text),
        "cores": extract_cores(text),
        "conductor": extract_conductor(text),
        "insulation_type": extract_insulation(text),
        "flame_type": extract_flame_type(text),
        "standard": extract_standard(text)
    }

    # ---------------- CLEAN NULLS ----------------
    structured = {k: v for k, v in structured.items() if v is not None}

    return {
        "structured": structured,
        "organizations": list(entities["organizations"]),
        "standards": list(entities["standards"])
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    sample_text = """
    3 core 150 sq mm copper XLPE FRLS cable rated 1.1 KV as per IS 8130.
    Manufactured by Polycab.
    """

    result = extract_entities(sample_text)

    import json
    print("\n=== NER OUTPUT ===\n")
    print(json.dumps(result, indent=4))