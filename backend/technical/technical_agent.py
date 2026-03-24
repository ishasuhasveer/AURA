from backend.technical.matching.ranking import rank_skus_by_spec_match
from backend.technical.explainability.comparison_table import build_explainability_table


class TechnicalAgent:
    """
    Technical Agent responsible for:
    - Evaluating OEM SKUs against RFP technical requirements
    - Computing Spec Match %
    - Producing explainable compliance tables
    """

    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    def evaluate(self, rfp_spec: dict, skus: list) -> list:
        """
        Run technical evaluation for a given RFP.

        Returns a list of Top-K SKU evaluation results.
        """

        ranked_skus = rank_skus_by_spec_match(
            rfp_spec=rfp_spec,
            skus=skus,
            top_k=self.top_k
        )

        # Attach explainability tables
        for result in ranked_skus:
            result["compliance_table"] = build_explainability_table(
                result["explanation"]
            )

        return ranked_skus


# --------------------------------------------------
# ORCHESTRATOR ENTRY POINT
# --------------------------------------------------

def run_technical_agent(rfp_data: dict) -> dict:
    """
    Entry point used by the orchestrator.

    Input:
        rfp_data (from parser)

    Output:
        JSON-safe technical evaluation results
    """

    # ---------------- EXTRACT RFP REQUIREMENTS ----------------
    tech_req = rfp_data.get("technical_requirements", {})

    rfp_spec = {
        "voltage": tech_req.get("voltage"),
        "conductor": tech_req.get("conductor"),
        "standard": tech_req.get("standard"),
    }

    # ---------------- SAMPLE SKU DATABASE ----------------
    # (Replace later with real datasheet parsing)
    skus = [
        {
            "sku_id": "SKU_001",
            "voltage": "11kV",
            "conductor": "copper",
            "standard": "IEC",
        },
        {
            "sku_id": "SKU_002",
            "voltage": "33kV",
            "conductor": "aluminium",
            "standard": "IEC",
        }
    ]

    # ---------------- RUN AGENT ----------------
    agent = TechnicalAgent(top_k=3)

    results = agent.evaluate(
        rfp_spec=rfp_spec,
        skus=skus
    )

    # ---------------- FORMAT OUTPUT ----------------
    formatted_results = []

    for r in results:
        formatted_results.append({
            "sku_id": r["sku_id"],
            "spec_match_percent": r["spec_match_percent"],
            "compliance_table": r["compliance_table"].to_dict(orient="records")
        })

    return {
        "recommended_skus": formatted_results
    }