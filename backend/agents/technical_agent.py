from backend.technical.technical_agent import TechnicalAgent


def run_technical_agent(rfp_spec: dict, skus: list) -> dict:


    agent = TechnicalAgent(top_k=3)

    ranked_results = agent.evaluate(rfp_spec, skus)

    formatted_results = []

    for result in ranked_results:
        formatted_results.append({
            "sku_id": result["sku_id"],
            "spec_match_percent": result["spec_match_percent"],
            "compliance_table": (
                result["compliance_table"].to_dict(orient="records")
                if hasattr(result["compliance_table"], "to_dict")
                else result["compliance_table"]
            )
        })

    return {
        "recommended_skus": formatted_results
    }