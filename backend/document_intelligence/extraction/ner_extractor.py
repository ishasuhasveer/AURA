import spacy
from typing import List, Dict


# Load spaCy model once
nlp = spacy.load("en_core_web_sm")


def extract_entities_from_chunks(chunks: List[str]) -> Dict[str, list]:
    """
    Extract entities from text chunks using spaCy NER.
    """

    entities = {
        "ORG": set(),        # Manufacturers, organizations
        "QUANTITY": set(),   # Measurements
        "PRODUCT": set(),    # Custom label via heuristics
        "MATERIAL": set()    # Custom label via heuristics
    }

    for chunk in chunks:
        doc = nlp(chunk)

        # Standard spaCy entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "QUANTITY"]:
                entities[ent.label_].add(ent.text)

        # Heuristic-based enrichment (important for specs)
        for token in doc:
            if token.text.upper() in ["COPPER", "ALUMINIUM", "PVC", "HDPE", "XLPE"]:
                entities["MATERIAL"].add(token.text.upper())

            if "CABLE" in token.text.upper():
                entities["PRODUCT"].add(token.text)

    return {k: sorted(list(v)) for k, v in entities.items()}
