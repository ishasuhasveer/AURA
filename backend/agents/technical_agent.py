from backend.database.mongo_client import db


def run_technical_agent(nlp_output: dict) -> dict:
    """
    Core Technical Engine

    Supports BOTH formats:
    1. Dict:
        {"voltage_kv": 2, "insulation_type": "FRLS"}

    2. List:
        [{"parameter": "voltage_kv", "value": 2}]
    """

    raw_requirements = nlp_output.get("technical_requirements", {})

    # --------------------------------------------------
    # 🔥 NORMALIZE INPUT → DICT FORMAT
    # --------------------------------------------------
    if isinstance(raw_requirements, dict):
        rfp_spec = raw_requirements

    elif isinstance(raw_requirements, list):
        rfp_spec = {
            item["parameter"]: item["value"]
            for item in raw_requirements
            if isinstance(item, dict) and "parameter" in item
        }

    else:
        rfp_spec = {}

    # 🚫 No usable requirements
    if not rfp_spec:
        return {
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }

    # --------------------------------------------------
    # FETCH SKUs
    # --------------------------------------------------
    sku_objects = list(db["products"].find({}))

    if not sku_objects:
        return {
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }

    results = []

    # --------------------------------------------------
    # MATCHING LOGIC
    # --------------------------------------------------
    for sku in sku_objects:

        sku_id = sku.get("sku_id")
        specs = sku.get("specs", {})

        total = len(rfp_spec)
        score = 0
        row_table = []

        for param, value in rfp_spec.items():

            sku_value = specs.get(param)

            # ---------------- MATCH LOGIC ----------------
            if sku_value is None:
                match = "Missing"
                points = 0

            elif str(sku_value).lower() == str(value).lower():
                match = "Exact"
                points = 1

            else:
                # simple partial logic
                if str(value).lower() in str(sku_value).lower():
                    match = "Partial"
                    points = 0.5
                else:
                    match = "Mismatch"
                    points = 0

            score += points

            row_table.append({
                "parameter": param,
                "rfp_value": value,
                "sku_value": sku_value if sku_value is not None else "Not Available",
                "match": match
            })

        # Avoid division by zero
        match_percent = round((score / total) * 100, 2) if total > 0 else 0

        results.append({
            "sku_id": sku_id,
            "match_percent": match_percent,
            "table": row_table
        })

    # --------------------------------------------------
    # RANKING
    # --------------------------------------------------
    results = sorted(results, key=lambda x: x["match_percent"], reverse=True)

    top3 = results[:3]

    return {
        "recommended_skus": [r["sku_id"] for r in top3],
        "spec_match_scores": {
            r["sku_id"]: r["match_percent"] for r in top3
        },
        "comparison_table": top3
    }