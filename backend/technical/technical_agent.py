from backend.technical.matching.ranking import rank_skus_by_spec_match
from backend.technical.explainability.comparison_table import build_explainability_table
from backend.database.mongo_client import get_all_products

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

    rfp_spec = tech_req

    # ---------------- FETCH REAL SKUs ----------------
    skus = get_all_products()

    # ---------------- RUN AGENT ----------------
    agent = TechnicalAgent(top_k=3)

    results = agent.evaluate(
        rfp_spec=rfp_spec,
        skus=skus
    )

    # ---------------- FORMAT OUTPUT ----------------
    recommended = []
    scores = {}
    comparison_tables = []

    for r in results:
        sku_id = r["sku_id"]

        recommended.append(sku_id)
        scores[sku_id] = r["spec_match_percent"]

        comparison_tables.append({
            "sku_id": sku_id,
            "table": r["compliance_table"].to_dict(orient="records")
        })

    return {
        "recommended_skus": recommended,
        "spec_match_scores": scores,
        "comparison_table": comparison_tables
    }