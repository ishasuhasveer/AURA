from backend.technical.matching.ranking import rank_skus_by_spec_match
from backend.technical.explainability.comparison_table import build_explainability_table
from backend.database.mongo_client import get_all_products


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_rfp_specs(rfp_input):
    """
    Converts:
    [{"parameter": "voltage_kv", "value": 2}]
    → {"voltage_kv": 2}
    """
    if isinstance(rfp_input, list):
        return {item["parameter"]: item["value"] for item in rfp_input}
    return rfp_input


# --------------------------------------------------
# TECHNICAL AGENT
# --------------------------------------------------

class TechnicalAgent:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    def evaluate(self, rfp_spec: dict, skus: list) -> list:

        # 🔥 FIX 1: Normalize input
        rfp_spec = normalize_rfp_specs(rfp_spec)

        ranked_skus = rank_skus_by_spec_match(
            rfp_spec=rfp_spec,
            skus=skus,
            top_k=self.top_k
        )

        final_results = []

        for result in ranked_skus:
            table_df = build_explainability_table(result["explanation"])

            final_results.append({
                "sku_id": result["sku_id"],
                "match_percent": result["spec_match_percent"],
                "price": result.get("price"),

                # JSON-safe table
                "comparison_table": table_df.to_dict(orient="records")
            })

        return final_results


# --------------------------------------------------
# ORCHESTRATOR ENTRY POINT
# --------------------------------------------------

def run_technical_agent(rfp_data: dict) -> dict:

    # ---------------- EXTRACT ----------------
    tech_req = rfp_data.get("technical_requirements", {})

    # ---------------- FETCH PRODUCTS ----------------
    skus = get_all_products()

    # 🔥 SAFETY: Ensure schema consistency
    cleaned_skus = []
    for sku in skus:
        cleaned_skus.append({
            "sku_id": sku.get("sku_id"),
            "specs": sku.get("specs", {}),
            "price": sku.get("price")
        })

    # ---------------- RUN AGENT ----------------
    agent = TechnicalAgent(top_k=3)

    results = agent.evaluate(
        rfp_spec=tech_req,
        skus=cleaned_skus
    )

    # ---------------- FINAL OUTPUT ----------------
    return {
        "technical_evaluation": results
    }