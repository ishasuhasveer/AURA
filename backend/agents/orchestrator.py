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

        print(f"Starting RFP workflow for {file_path}")

        # ✅ FINAL STATE aligned with workflow
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

            print("Workflow completed successfully")

            return self.aggregate_results(final_state)

        except Exception as e:
            print(f"Workflow failed: {type(e).__name__}: {str(e)}")

            print("\n===== FULL TRACEBACK =====")
            traceback.print_exc()
            print("==========================\n")

            raise RuntimeError(f"RFP processing failed: {str(e)}")

    def aggregate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate agent outputs into final API response.
        """

        return {
            "rfp_summary": state.get("sales", {}),
            "technical_summary": state.get("technical", {}),
            "pricing_summary": state.get("pricing", {})
        }