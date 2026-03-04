from backend.pricing.pricing_engine import compute_pricing


class PricingAgent:

    def run(self, technical_output: dict, quantities: dict) -> dict:
        """
        Entry point for pricing agent.
        """

        recommended_skus = technical_output.get("recommended_skus", [])

        pricing_result = compute_pricing(
            recommended_skus=recommended_skus,
            quantities=quantities
        )

        return pricing_result