from backend.technical.explainability.comparison_table import (
    build_explainability_table
)


def test_explainability_table():
    explanation = [
        {
            "spec": "voltage",
            "category": "mandatory",
            "rfp_value": "400 kV",
            "sku_value": "400 kV",
            "score": 1.0
        },
        {
            "spec": "armouring",
            "category": "optional",
            "rfp_value": "Armoured",
            "sku_value": "Unarmoured",
            "score": 0.0
        }
    ]

    df = build_explainability_table(explanation)

    assert not df.empty
    assert "compliance_status" in df.columns
    assert df.loc[0, "compliance_status"] == "Compliant"
    assert df.loc[1, "compliance_status"] == "Non-Compliant"
