from decision_intelligence.technical_agent import TechnicalAgent


def main():
    # ---------------- RFP ----------------
    rfp_spec = {
        "rfp_id": "RFP_2024_001",
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

    # ---------------- SKUs ----------------
    skus = [
        {
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
        },
        {
            "sku_id": "SKU_002",
            "voltage": "400 kV",
            "conductor": "ALUMINIUM",
            "insulation": "XLPE",
            "standard": "IEC 60502",
            "attributes": {
                "cross_section_mm2": 70,
                "armouring": "Armoured",
                "core_count": None
            }
        }
    ]

    # ---------------- AGENT ----------------
    agent = TechnicalAgent(top_k=2)
    results = agent.evaluate(rfp_spec, skus)

    # ---------------- OUTPUT ----------------
    print("\n========= TECHNICAL AGENT OUTPUT =========\n")

    for idx, res in enumerate(results, start=1):
        print(f"Rank #{idx}")
        print(f"SKU ID       : {res['sku_id']}")
        print(f"Spec Match % : {res['spec_match_percent']}%")
        print("\nCompliance Table:")
        print(res["compliance_table"].to_string(index=False))
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()