from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# Agents
from backend.agents.sales_agent import SalesAgent
from backend.agents.pricing_agent import PricingAgent

# External pipelines
from backend.document_intelligence.rfp_parser import parse_rfp
from backend.agents.technical_agent import run_technical_agent


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
def sales_node(state):
    try:
        print("\n--- SALES NODE START ---")

        agent = SalesAgent()

        output = agent.process_rfp(
            state["file_path"],
            state["extracted_text"]
        )

        print("SALES OUTPUT:", output)

        state["sales"] = output

        print("--- SALES NODE END ---\n")

        return state

    except Exception as e:
        print("❌ SALES NODE ERROR:", str(e))
        raise

# ----------------------------
# NLP NODE (ANMOL PIPELINE)
# ----------------------------
def nlp_node(state):
    try:
        print("\n--- NLP NODE START ---")

        rfp_json = parse_rfp(state["file_path"])

        print("NLP OUTPUT:", rfp_json)
        print("TYPE:", type(rfp_json))

        state["nlp"] = rfp_json

        print("--- NLP NODE END ---\n")

        return state

    except Exception as e:
        print("❌ NLP NODE ERROR:", str(e))
        raise


# ----------------------------
# TECHNICAL NODE (ISHA LOGIC)
# ----------------------------
def technical_node(state):
    try:
        print("\n--- TECHNICAL NODE START ---")

        print("INPUT NLP:", state["nlp"])

        output = run_technical_agent(state["nlp"])

        print("TECH OUTPUT:", output)

        state["technical"] = output

        print("--- TECHNICAL NODE END ---\n")

        return state

    except Exception as e:
        print("❌ TECHNICAL NODE ERROR:", str(e))
        raise


# ----------------------------
# PRICING NODE (BHARGAV)
# ----------------------------
def pricing_node(state):
    try:
        print("\n--- PRICING NODE START ---")

        print("TECH INPUT:", state["technical"])
        print("NLP INPUT:", state["nlp"])

        pricing_agent = PricingAgent()

        quantities = state["nlp"].get("quantities", {})

        output = pricing_agent.run(
            technical_output=state["technical"],
            quantities=quantities
        )

        print("PRICING OUTPUT:", output)

        state["pricing"] = output

        print("--- PRICING NODE END ---\n")

        return state

    except Exception as e:
        print("❌ PRICING NODE ERROR:", str(e))
        raise


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