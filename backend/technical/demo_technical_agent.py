# backend/technical/demo_technical_agent.py

from backend.technical.technical_agent import TechnicalAgent


def run_technical_agent(rfp_data: dict) -> dict:
    """
    Entry point used by orchestrator.

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

    # ---------------- SAMPLE SKU DATABASE (for demo) ----------------
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

    # ---------------- RUN TECHNICAL AGENT ----------------
    agent = TechnicalAgent(top_k=2)

    results = agent.evaluate(rfp_spec, skus)

    # ---------------- FORMAT OUTPUT (IMPORTANT) ----------------
    formatted_results = []

    for res in results:
        formatted_results.append({
            "sku_id": res["sku_id"],
            "spec_match_percent": res["spec_match_percent"],
            "compliance_table": res["compliance_table"].to_dict(orient="records")
        })

    return {
        "recommended_skus": formatted_results
    }


# -------------------------------
# MANUAL TEST
# -------------------------------
if __name__ == "__main__":

    # Simulating parser output
    sample_rfp_data = {
        "rfp_id": "RFP_001",
        "technical_requirements": {
            "voltage": "11kV",
            "conductor": "copper",
            "standard": "IEC"
        },
        "quantities": {
            "estimated_quantity": 100
        }
    }

    result = run_technical_agent(sample_rfp_data)

    import json
    print(json.dumps(result, indent=4))