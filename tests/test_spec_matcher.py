from backend.technical.matching.spec_match import compute_spec_match


def test_spec_match_engine():
    rfp_spec = {
        "rfp_id": "RFP_001",
        "voltage": "400 kV",
        "conductor": "COPPER",
        "insulation": "XLPE",
        "standard": "IEC 60502",
        "attributes": {
            "cross_section_mm2": 50,
            "armouring": "Armoured",
            "core_count": None
        }
    }

    sku = {
        "sku_id": "SKU_001",
        "voltage": "400 kV",
        "conductor": "COPPER",
        "insulation": "XLPE",
        "standard": "IEC 60502",
        "attributes": {
            "cross_section_mm2": 50,
            "armouring": "Unarmoured",
            "core_count": None
        }
    }

    score, explanation = compute_spec_match(rfp_spec, sku)

    assert score > 0
    assert isinstance(explanation, list)
    assert len(explanation) == 6
