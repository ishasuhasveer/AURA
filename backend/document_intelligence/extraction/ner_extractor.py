import spacy
from typing import List, Dict

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str) -> Dict:
    """
    Extract relevant entities (structured)
    """

    doc = nlp(text)

    entities = {
        "materials": set(),
        "organizations": set(),
        "measurements": set()
    }

    for ent in doc.ents:

        if ent.label_ in ["ORG"]:
            entities["organizations"].add(ent.text)

        if ent.label_ in ["QUANTITY"]:
            entities["measurements"].add(ent.text)

        # Custom filtering for materials
        if any(word in ent.text.upper() for word in ["COPPER", "PVC", "HDPE", "XLPE"]):
            entities["materials"].add(ent.text.upper())

    # Convert sets → lists
    return {k: list(v) for k, v in entities.items()}


# -------------------------------
# TEST BLOCK
# -------------------------------
if __name__ == "__main__":

    sample_text = """
    25 core copper cable with HDPE insulation rated for 3 KV as per IS 8130.
    Manufactured by Polycab and CMI.
    """

    result = extract_entities(sample_text)

    import json

    print("\n=== NER OUTPUT ===\n")
    print(json.dumps(result, indent=4))