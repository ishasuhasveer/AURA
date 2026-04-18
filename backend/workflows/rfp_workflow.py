from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# Agents
from backend.agents.sales_agent import SalesAgent
from backend.agents.pricing_agent import PricingAgent
from backend.agents.technical_agent import run_technical_agent

# NLP
from backend.document_intelligence.rfp_parser import parse_rfp


# ----------------------------
# STATE DEFINITION
# ----------------------------
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


# ----------------------------
# NLP NODE
# ----------------------------
def nlp_node(state):
    print("\n--- NLP NODE START ---")

    rfp_json = parse_rfp(state["file_path"])

    print("NLP OUTPUT:", rfp_json)

    if not rfp_json:
        raise ValueError("❌ NLP returned empty output")

    state["nlp"] = rfp_json

    print("--- NLP NODE END ---\n")
    return state


# ----------------------------
# TECHNICAL NODE (FINAL)
# ----------------------------
def technical_node(state):
    print("\n--- TECHNICAL NODE START ---")

    nlp_output = state.get("nlp", {}) or {}
    print("INPUT NLP:", nlp_output)

    tech_req = nlp_output.get("technical_requirements") or {}
    summary = nlp_output.get("summary") or {}
    category = summary.get("category", "unknown")

    print("EXTRACTED TECH REQ:", tech_req)
    print("CATEGORY:", category)

    ALLOWED_CATEGORIES = ["cable_supply", "electrical_fittings"]

    # ❌ Unsupported category
    if category not in ALLOWED_CATEGORIES:
        print(f"⚠️ Skipping Technical Agent → Unsupported category: {category}")

        state["technical"] = {
            "status": "skipped",
            "reason": f"{category}_not_supported",
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }

        return state

    # ❌ No requirements
    if not isinstance(tech_req, dict) or len(tech_req) == 0:
        print("⚠️ No technical requirements → skipping")

        state["technical"] = {
            "status": "skipped",
            "reason": "no_requirements_found",
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }

        return state

    # ✅ Run agent
    try:
        output = run_technical_agent({
            "technical_requirements": tech_req
        })

    except Exception as e:
        print("❌ Technical Agent crashed:", str(e))

        state["technical"] = {
            "status": "failed",
            "reason": str(e),
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }

        return state

    if not output:
        state["technical"] = {
            "status": "failed",
            "reason": "empty_output",
            "recommended_skus": [],
            "spec_match_scores": {},
            "comparison_table": []
        }
        return state

    print("TECH OUTPUT:", output)

    state["technical"] = output

    print("--- TECHNICAL NODE END ---\n")
    return state


# ----------------------------
# PRICING NODE
# ----------------------------
def pricing_node(state):
    print("\n--- PRICING NODE START ---")

    tech = state.get("technical", {})
    nlp = state.get("nlp", {})

    if not tech:
        raise ValueError("❌ No Technical output for Pricing Agent")

    pricing_agent = PricingAgent()

    quantities = nlp.get("quantities") or {"default": 1}

    output = pricing_agent.run(
        technical_output=tech,
        quantities=quantities
    )

    print("PRICING OUTPUT:", output)

    state["pricing"] = output

    print("--- PRICING NODE END ---\n")
    return state


# ----------------------------
# GRAPH BUILDER (🔥 THIS WAS MISSING)
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