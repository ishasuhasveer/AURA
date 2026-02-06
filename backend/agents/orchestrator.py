from typing import Dict, Any
from agents.sales_agent import SalesAgent

class MainOrchestrator:
    def __init__(self):
        self.state = {
            "sales_done": False,
            "nlp_done": False,
            "technical_done": False,
            "pricing_done": False
        }

        self.results = {}


def start_workflow(self, file_path: str, extracted_text: str) -> Dict[str, Any]:
    self.trigger_sales_agent(file_path, extracted_text)
    self.trigger_document_pipeline()
    self.trigger_technical_agent()
    self.trigger_pricing_agent()

    return self.aggregate_results()


def trigger_sales_agent(self, file_path: str, extracted_text: str):
    if self.state["sales_done"]:
        raise RuntimeError("Sales agent already executed")

    sales_agent = SalesAgent()
    sales_output = sales_agent.process_rfp(file_path, extracted_text)

    self.results["sales"] = sales_output
    self.state["sales_done"] = True


def trigger_document_pipeline(self):
    if not self.state["sales_done"]:
        raise RuntimeError("Sales must complete before NLP")

    # Placeholder NLP output
    self.results["nlp"] = {
        "technical_requirements": [],
        "quantities": {},
        "testing_requirements": []
    }

    self.state["nlp_done"] = True


def trigger_technical_agent(self):
    if not self.state["nlp_done"]:
        raise RuntimeError("NLP must complete before Technical Agent")

    self.results["technical"] = {
        "recommended_skus": [],
        "spec_match_scores": {}
    }

    self.state["technical_done"] = True


def trigger_pricing_agent(self):
    if not self.state["technical_done"]:
        raise RuntimeError("Technical must complete before Pricing")

    self.results["pricing"] = {
        "total_estimated_cost": 0
    }

    self.state["pricing_done"] = True


def aggregate_results(self) -> Dict[str, Any]:
    if not all(self.state.values()):
        raise RuntimeError("Workflow incomplete")

    return {
        "rfp_summary": self.results.get("sales"),
        "technical_summary": self.results.get("technical"),
        "pricing_summary": self.results.get("pricing")
    }

if __name__ == "__main__":
    orchestrator = MainOrchestrator()

    dummy_text = """
    RFP for electrical cable supply.
    Deadline: 15 February 2026
    """

    output = orchestrator.start_workflow("sample.pdf", dummy_text)
    print(output)