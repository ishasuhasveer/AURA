import pandas as pd


def build_explainability_table(explanation: dict) -> pd.DataFrame:
    """
    Convert spec match explanation dict into a
    human-readable compliance table.
    """

    if not explanation:
        return pd.DataFrame()

    # --------------------------------------------
    # Convert dict → list of rows
    # --------------------------------------------
    rows = []

    for spec, values in explanation.items():
        rows.append({
            "spec": spec,
            "rfp_value": values.get("rfp"),
            "sku_value": values.get("sku"),
            "score": values.get("score")
        })

    df = pd.DataFrame(rows)

    # --------------------------------------------
    # Add compliance status
    # --------------------------------------------
    def compliance_label(score):
        if score == 1:
            return "Compliant"
        elif score == 0.5:
            return "Partially Compliant"
        else:
            return "Non-Compliant"

    df["compliance_status"] = df["score"].apply(compliance_label)

    # --------------------------------------------
    # Optional: sort by importance (score)
    # --------------------------------------------
    df = df.sort_values(by="score", ascending=False)

    return df