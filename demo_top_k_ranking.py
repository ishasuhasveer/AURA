from decision_intelligence.spec_matching.sku_ranker import rank_skus_by_spec_match
from decision_intelligence.spec_matching.explanation_table import build_explainability_table


def main():
    # ---------------- RFP SPEC ----------------
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

    # ---------------- SKU LIST ----------------
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
        },
        {
            "sku_id": "SKU_003",
            "voltage": "220 kV",
            "conductor": "COPPER",
            "insulation": "XLPE",
            "standard": "IEC 60502",
            "attributes": {
                "cross_section_mm2": 50,
                "armouring": "Armoured",
                "core_count": None
            }
        }
    ]

    # ---------------- RANKING ----------------
    ranked_skus = rank_skus_by_spec_match(
        rfp_spec=rfp_spec,
        skus=skus,
        top_k=3
    )

    # ---------------- PRINT OUTPUT ----------------
    print("\n========== TOP-K SKU RANKING ==========\n")

    for idx, result in enumerate(ranked_skus, start=1):
        print(f"Rank #{idx}")
        print(f"SKU ID            : {result['sku_id']}")
        print(f"Spec Match %      : {result['spec_match_percent']}%")

        df = build_explainability_table(result["explanation"])
        print("\nCompliance Table:")
        print(df.to_string(index=False))

        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
