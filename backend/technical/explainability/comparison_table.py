import pandas as pd


def build_explainability_table(explanation: list) -> pd.DataFrame:
    """
    Convert spec match explanation rows into a
    human-readable compliance table.

    Input:
    - explanation: list of dicts from compute_spec_match()

    Output:
    - pandas DataFrame suitable for UI / export
    """

    if not explanation:
        return pd.DataFrame()

    df = pd.DataFrame(explanation)

    # --------------------------------------------
    # Add compliance status column
    # --------------------------------------------
    def compliance_label(row):
        if row["score"] == 1.0:
            return "Compliant"
        if row["score"] == 0.5:
            return "Partially Compliant"
        return "Non-Compliant"

    df["compliance_status"] = df.apply(compliance_label, axis=1)

    # --------------------------------------------
    # Reorder columns for readability
    # --------------------------------------------
    df = df[
        [
            "spec",
            "category",
            "rfp_value",
            "sku_value",
            "score",
            "compliance_status"
        ]
    ]

    return df
