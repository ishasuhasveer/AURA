from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from backend.agents.sales_agent import SalesAgent


class RFPState(TypedDict):
    file_path: str
    extracted_text: str

    sales: Dict[str, Any]
    nlp: Dict[str, Any]
    technical: Dict[str, Any]
    pricing: Dict[str, Any]

def sales_node(state: RFPState) -> RFPState:
    agent = SalesAgent()
    sales_output = agent.process_rfp(
        state["file_path"],
        state["extracted_text"]
    )

    state["sales"] = sales_output
    return state


def nlp_node(state: RFPState) -> RFPState:
    state["nlp"] = {
        "technical_requirements": [],
        "quantities": {},
        "testing_requirements": []
    }
    return state

def technical_node(state: RFPState) -> RFPState:
    state["technical"] = {
        "recommended_skus": [],
        "spec_match_scores": {}
    }
    return state

def pricing_node(state: RFPState) -> RFPState:
    state["pricing"] = {
        "total_estimated_cost": 0
    }
    return state

def build_rfp_graph():
    graph = StateGraph(RFPState)

    graph.add_node("sales", sales_node)
    graph.add_node("nlp", nlp_node)
    graph.add_node("technical", technical_node)
    graph.add_node("pricing", pricing_node)

    graph.set_entry_point("sales")

    graph.add_edge("sales", "nlp")
    graph.add_edge("nlp", "technical")
    graph.add_edge("technical", "pricing")
    graph.add_edge("pricing", END)

    return graph.compile()

if __name__ == "__main__":
    graph = build_rfp_graph()

    initial_state: RFPState = {
        "file_path": "sample.pdf",
        "extracted_text": """
        RFP for electrical cable supply.
        Deadline: 15 February 2026
        """,
        "sales": {},
        "nlp": {},
        "technical": {},
        "pricing": {}
    }

    final_state = graph.invoke(initial_state)
    print(final_state)