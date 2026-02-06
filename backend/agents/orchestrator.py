from typing import Dict, Any
from backend.workflows.rfp_workflow import build_rfp_graph


class MainOrchestrator:
    def __init__(self):
        self.graph = build_rfp_graph()

    def start_workflow(self, file_path: str, extracted_text: str) -> Dict[str, Any]:
        initial_state = {
            "file_path": file_path,
            "extracted_text": extracted_text,
            "sales": {},
            "nlp": {},
            "technical": {},
            "pricing": {}
        }

        final_state = self.graph.invoke(initial_state)

        return self.aggregate_results(final_state)

    def aggregate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "rfp_summary": state.get("sales"),
            "technical_summary": state.get("technical"),
            "pricing_summary": state.get("pricing")
        }

if __name__ == "__main__":
    orchestrator = MainOrchestrator()

    dummy_text = """
    RFP for electrical cable supply.
    Deadline: 15 February 2026
    """

    output = orchestrator.start_workflow("sample.pdf", dummy_text)
    print(output)