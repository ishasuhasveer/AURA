from backend.technical.technical_agent import TechnicalAgent


def run_technical_agent(nlp_output: dict) -> dict:

    print("\n===== DEBUG TECHNICAL AGENT START =====")

    # ---------------- INPUT ----------------
    print("NLP OUTPUT:", nlp_output)
    print("TYPE:", type(nlp_output))

    rfp_spec = nlp_output.get("technical_requirements", {})

    if not isinstance(rfp_spec, dict):
        raise ValueError("Invalid RFP spec format")

    print("RFP SPEC:", rfp_spec)
    print("TYPE:", type(rfp_spec))

    skus = [
        {
            "sku_id": "CU_3C_35_11KV",
            "voltage": 11,
            "conductor": "Copper",
            "standard": "IS"
        },
        {
            "sku_id": "AL_3C_50_11KV",
            "voltage": 11,
            "conductor": "Aluminum",
            "standard": "IS"
        },
        {
            "sku_id": "CU_3C_25_11KV",
            "voltage": 11,
            "conductor": "Copper",
            "standard": "IS"
        }
    ]

    agent = TechnicalAgent(top_k=3)

    # ---------------- CORE CALL ----------------
    ranked_results = agent.evaluate(rfp_spec, skus)

    print("RANKED RESULTS:", ranked_results)
    print("TYPE:", type(ranked_results))

    # 🔥 CRITICAL CHECK
    if isinstance(ranked_results, str):
        raise ValueError(f"TechnicalAgent returned STRING: {ranked_results}")

    if not isinstance(ranked_results, list):
        raise ValueError(f"Unexpected output type: {type(ranked_results)}")

    formatted_results = []

    for result in ranked_results:

        print("ITER RESULT:", result)
        print("TYPE:", type(result))

        if isinstance(result, str):
            formatted_results.append({
                "sku_id": result,
                "spec_match_percent": 0,
                "compliance_table": []
            })
            continue

        if isinstance(result, dict):
            formatted_results.append({
                "sku_id": result.get("sku_id"),
                "spec_match_percent": result.get("spec_match_percent", 0),
                "compliance_table": result.get("compliance_table", [])
            })
            continue

        raise ValueError(f"Invalid result format: {result}")

    print("===== DEBUG TECHNICAL AGENT END =====\n")

    return {
        "recommended_skus": formatted_results
    }