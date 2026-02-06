from decision_intelligence.spec_matching.rfp_schema import empty_rfp_spec


def test_empty_rfp_schema():
    rfp = empty_rfp_spec("RFP_TEST_001")

    assert rfp["rfp_id"] == "RFP_TEST_001"

    # Mandatory fields must exist
    assert rfp["voltage"] is None
    assert rfp["conductor"] is None
    assert rfp["insulation"] is None
    assert rfp["standard"] is None

    # Optional attributes must exist
    assert "attributes" in rfp
    assert rfp["attributes"]["core_count"] is None
    assert rfp["attributes"]["cross_section_mm2"] is None
    assert rfp["attributes"]["armouring"] is None

if __name__ == "__main__":
    test_empty_rfp_schema()
    print("RFP schema test passed")
