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

            # 🚨 VALIDATION (CRITICAL)
            if not final_state.get("nlp"):
                raise ValueError("❌ NLP output is empty → RFP not processed")

            if not final_state.get("technical"):
                raise ValueError("❌ Technical agent output missing")

            if not final_state.get("pricing"):
                raise ValueError("❌ Pricing agent output missing")

            # ⚠️ Detect static SKU bug
            tech = final_state.get("technical", {})
            skus = tech.get("recommended_skus", [])

            if isinstance(skus, list) and len(skus) > 1:
                first = skus[0]
                if all(s == first for s in skus):
                    print("⚠️ WARNING: All SKUs identical → static output bug likely")

            print("✅ Workflow completed successfully")

            return self.aggregate_results(final_state)

        except Exception as e:
            print(f"\n❌ Workflow failed: {type(e).__name__}: {str(e)}")

            print("\n===== FULL TRACEBACK =====")
            traceback.print_exc()
            print("==========================\n")

            raise RuntimeError(f"RFP processing failed: {str(e)}")

    def aggregate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate agent outputs into final API response.
        """

        technical = state.get("technical", {})
        pricing = state.get("pricing", {})

        return {
            "rfp_summary": state.get("sales", {}),

            # 🔥 CORE OUTPUT FOR YOUR UI TABLE
            "decision_table": technical.get("comparison_table", []),

            "top_sku_recommendations": technical.get("recommended_skus", []),

            "spec_match_scores": technical.get("spec_match_scores", {}),

            "pricing_summary": pricing
        }