from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from datetime import date
from backend.agents.sales_agent import SalesAgent
from backend.agents.pricing_agent import PricingAgent
from backend.technical.technical_agent import run_technical_agent


class RFPState(TypedDict):
    file_name: str
    rfp_data: Dict[str, Any]

    sales: Dict[str, Any]
    technical: Dict[str, Any]
    pricing: Dict[str, Any]


# ---------------- SALES NODE ----------------
def sales_node(state: RFPState) -> RFPState:

    agent = SalesAgent()

    rfp_data = state.get("rfp_data", {})


    enriched_text = f"""
    RFP Summary:
    Voltage: {rfp_data.get("technical_requirements", [{}])[0].get("voltage", "N/A")} kV
    Conductor: {rfp_data.get("technical_requirements", [{}])[0].get("conductor", "N/A")}
    Deadline: 2026-02-15
    """

    sales_output = agent.process_rfp(
        state["file_name"],
        enriched_text
    )

    if "deadline" not in sales_output or sales_output["deadline"] is None:
        sales_output["deadline"] = "2026-02-15"

    state["sales"] = sales_output
    return state

# ---------------- TECHNICAL NODE ----------------
def technical_node(state: RFPState) -> RFPState:

    rfp_data = state.get("rfp_data", {})

    technical_output = run_technical_agent(rfp_data)

    state["technical"] = technical_output

    return state


# ---------------- PRICING NODE ----------------
def pricing_node(state: RFPState) -> RFPState:

    pricing_agent = PricingAgent()

    quantities = state.get("rfp_data", {}).get("quantities", {})

    pricing_output = pricing_agent.run(
        technical_output=state["technical"],
        quantities=quantities
    )

    state["pricing"] = pricing_output

    return state


# ---------------- GRAPH ----------------
def build_rfp_graph():

    graph = StateGraph(RFPState)

    graph.add_node("sales", sales_node)
    graph.add_node("technical", technical_node)
    graph.add_node("pricing", pricing_node)

    graph.set_entry_point("sales")

    graph.add_edge("sales", "technical")
    graph.add_edge("technical", "pricing")
    graph.add_edge("pricing", END)

    return graph.compile()