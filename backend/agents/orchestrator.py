from typing import Dict, Any
from backend.workflows.rfp_workflow import build_rfp_graph
from backend.config import log


class MainOrchestrator:

    def __init__(self):
        log("Initializing LangGraph workflow")
        self.graph = build_rfp_graph()

        if self.graph is None:
            raise RuntimeError("LangGraph workflow initialization failed")

    def start_workflow(self, file_name: str, rfp_data: Dict[str, Any]) -> Dict[str, Any]:

        log(f"Starting RFP workflow for {file_name}")

        # 🔥 FIX: use structured rfp_data directly
        initial_state = {
            "file_name": file_name,
            "rfp_data": rfp_data,
            "sales": {},
            "technical": {},
            "pricing": {}
        }

        try:
            final_state = self.graph.invoke(initial_state)

            log("Workflow completed successfully")

            return self.aggregate_results(final_state)

        except Exception as e:
            log(f"Workflow failed: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"RFP processing failed: {str(e)}")

    def aggregate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate agent outputs into final API response.
        """

        return {
            "rfp_summary": state.get("sales", {}),
            "technical_results": state.get("technical", {}),
            "pricing_results": state.get("pricing", {})
        }