# backend/agents/orchestrator.py

import traceback
from typing import Dict, Any
from backend.workflows.rfp_workflow import build_rfp_graph


class MainOrchestrator:

    def __init__(self):
        print("Initializing LangGraph workflow")

        self.graph = build_rfp_graph()

        if self.graph is None:
            raise RuntimeError("LangGraph workflow initialization failed")

    def start_workflow(self, file_path: str, extracted_text: str) -> Dict[str, Any]:

        print(f"\n🚀 Starting RFP workflow for: {file_path}")

        # ✅ Initial State
        initial_state = {
            "file_path": file_path,
            "extracted_text": extracted_text,
            "sales": {},
            "nlp": {},
            "technical": {},
            "pricing": {}
        }

        try:
            final_state = self.graph.invoke(initial_state)

            print("\n===== DEBUG STATE OUTPUT =====")
            print("Sales Output:\n", final_state.get("sales"))
            print("\nNLP Output:\n", final_state.get("nlp"))
            print("\nTechnical Output:\n", final_state.get("technical"))
            print("\nPricing Output:\n", final_state.get("pricing"))
            print("================================\n")

            # 🚨 VALIDATION
            if not final_state.get("nlp"):
                raise ValueError("❌ NLP output is empty → RFP not processed")

            if not final_state.get("technical"):
                raise ValueError("❌ Technical agent output missing")

            if not final_state.get("pricing"):
                raise ValueError("❌ Pricing agent output missing")

            # 🚨 STATIC SKU CHECK (UPDATED)
            tech = final_state.get("technical", {})
            skus = tech.get("recommended_skus", [])

            if isinstance(skus, list) and len(skus) > 1:
                ids = [
                    s.get("sku_config_id") if isinstance(s, dict) else s
                    for s in skus
                ]
                if len(set(ids)) == 1:
                    print("⚠️ WARNING: All SKUs identical → static output bug likely")

            # 🚨 PRICING CONSISTENCY CHECK
            pricing = final_state.get("pricing", {})
            if pricing.get("pricing_details"):
                for item in pricing["pricing_details"]:
                    if not item.get("sku_config_id"):
                        print("⚠️ WARNING: Pricing item missing sku_config_id")

            print("✅ Workflow completed successfully")

            return self.aggregate_results(final_state)

        except Exception as e:
            print(f"\n❌ Workflow failed: {type(e).__name__}: {str(e)}")

            print("\n===== FULL TRACEBACK =====")
            traceback.print_exc()
            print("==========================\n")

            raise RuntimeError(f"RFP processing failed: {str(e)}")

    def aggregate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:

        technical = state.get("technical", {})
        pricing = state.get("pricing", {})

        decision_table = []
        scores = {}

        # 🔥 Extract from requirements_mapping
        if technical.get("requirements_mapping"):

            decision_table = technical["requirements_mapping"]

            for req in decision_table:
                for sku in req.get("top_matches", []):

                    sku_config_id = sku.get("sku_config_id")
                    match = sku.get("match_percent", 0)

                    if not sku_config_id:
                        continue

                    if sku_config_id not in scores or scores[sku_config_id] < match:
                        scores[sku_config_id] = match

        # 🔥 Sort SKUs
        top_skus = sorted(
            scores.keys(),
            key=lambda x: scores.get(x, 0),
            reverse=True
        )

        # 🚨 EMPTY SAFETY CHECK
        if not decision_table and not technical.get("error"):
            print("⚠️ WARNING: No decision table but no error flagged")

        return {
            "rfp_summary": state.get("sales", {}),

            "decision_table": decision_table,

            "top_sku_recommendations": [
                {
                    "sku_config_id": sku,
                    "match_percent": scores.get(sku)
                }
                for sku in top_skus[:5]
            ],

            "spec_match_scores": scores,

            "pricing_summary": pricing,

            # 🔥 TECHNICAL OUTPUTS
            "error": technical.get("error"),
            "analysis": technical.get("analysis"),
            "suggested_skus": technical.get("suggested_skus"),
            "recommendation": technical.get("recommendation"),
            "status": technical.get("status", "success")
        }