from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# Agents
from backend.agents.sales_agent import SalesAgent
from backend.agents.pricing_agent import PricingAgent

# External pipelines
from backend.document_intelligence.rfp_parser import parse_rfp
from backend.technical.technical_agent import run_technical_agent


class RFPState(TypedDict):
    file_path: str
    extracted_text: str

    sales: Dict[str, Any]
    nlp: Dict[str, Any]
    technical: Dict[str, Any]
    pricing: Dict[str, Any]


# ----------------------------
# SALES NODE
# ----------------------------
def sales_node(state: RFPState) -> RFPState:
    agent = SalesAgent()

    sales_output = agent.process_rfp(
        state["file_path"],
        state["extracted_text"]
    )

    state["sales"] = sales_output
    return state


# ----------------------------
# NLP NODE (ANMOL PIPELINE)
# ----------------------------
def nlp_node(state: RFPState) -> RFPState:

    rfp_json = parse_rfp(state["file_path"])

    state["nlp"] = rfp_json

    return state


# ----------------------------
# TECHNICAL NODE (ISHA LOGIC)
# ----------------------------
def technical_node(state: RFPState) -> RFPState:

    technical_output = run_technical_agent(state["nlp"])

    state["technical"] = technical_output

    return state


# ----------------------------
# PRICING NODE (BHARGAV)
# ----------------------------
def pricing_node(state: RFPState) -> RFPState:

    pricing_agent = PricingAgent()

    quantities = state["nlp"].get("quantities", {})

    pricing_output = pricing_agent.run(
        technical_output=state["technical"],
        quantities=quantities
    )

    state["pricing"] = pricing_output

    return state


# ----------------------------
# GRAPH BUILDER
# ----------------------------
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


# ----------------------------
# LOCAL TEST
# ----------------------------
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

    print("\nFINAL STATE:\n")
    print(final_state)