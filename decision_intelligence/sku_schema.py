from typing import Dict, Any


def empty_sku(sku_id: str, source_document: str) -> Dict[str, Any]:
    """
    Create an empty normalized SKU object.
    Fields are populated only when confidently extracted.
    """
    return {
        "sku_id": sku_id,
        "voltage": None,
        "conductor": None,
        "insulation": None,
        "standard": None,
        "attributes": {
            "core_count": None,
            "cross_section_mm2": None,
            "armouring": None
        },
        "source": {
            "document": source_document,
            "extraction_method": "deterministic"
        }
    }


if __name__ == "__main__":
    sku = empty_sku(
        sku_id="SAMPLE_CABLE_001",
        source_document="sample_cable.pdf"
    )
    print(sku)
