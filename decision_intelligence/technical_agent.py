from decision_intelligence.spec_matching.sku_ranker import rank_skus_by_spec_match
from decision_intelligence.spec_matching.explanation_table import build_explainability_table


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