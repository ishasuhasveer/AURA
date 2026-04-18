import pandas as pd


def build_explainability_table(explanation: dict) -> pd.DataFrame:
    """
    Convert spec match explanation dict into a
    human-readable compliance table.
    """

    if not explanation:
        return pd.DataFrame()

    rows = []

    for spec, values in explanation.items():
        rows.append({
            "parameter": spec,
            "mapped_to": values.get("mapped_to"),

            # 🔥 FIXED KEYS
            "rfp_value": values.get("rfp_value"),
            "sku_value": values.get("sku_value"),

            # 🔥 HUMAN READABLE
            "match_type": values.get("gap"),

            # keep score for sorting (optional)
            "score": values.get("score")
        })

    df = pd.DataFrame(rows)

    # --------------------------------------------
    # Sort by importance
    # --------------------------------------------
    df = df.sort_values(by="score", ascending=False)

    # --------------------------------------------
    # Drop score from final UI (optional)
    # --------------------------------------------
    df = df.drop(columns=["score"])

    return df