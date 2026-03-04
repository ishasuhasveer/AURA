from typing import Dict, Any
from backend.workflows.rfp_workflow import build_rfp_graph
from backend.config import log


class MainOrchestrator:

    def __init__(self):
        log("Initializing LangGraph workflow")
        self.graph = build_rfp_graph()

    def start_workflow(self, file_path: str, extracted_text: str) -> Dict[str, Any]:

        log("Starting RFP workflow")

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

            log("Workflow completed successfully")

            return self.aggregate_results(final_state)

        except Exception as e:
            log(f"Workflow failed: {str(e)}")
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