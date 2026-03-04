import streamlit as st
import requests
import pandas as pd


# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AURA — Agentic RFP Assistant",
    layout="wide"
)

# -------------------------------
# Header
# -------------------------------
st.title("📄 AURA — Agentic RFP Response Automation")

st.caption(
    "An Agentic AI system for automated RFP qualification, "
    "technical compliance analysis, and pricing estimation"
)

st.markdown("---")


# -------------------------------
# Backend Configuration
# -------------------------------
BACKEND_URL = "http://127.0.0.1:8000/process-rfp"


# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("🧠 System Overview")

    st.markdown(
        """
        **AURA** simulates how an industrial OEM responds to B2B RFPs.

        **Agentic Workflow**
        - Sales Agent → Qualification
        - Document Intelligence → RFP Parsing
        - Technical Agent → SKU Matching
        - Pricing Agent → Cost Estimation

        **Tech Stack**
        - FastAPI
        - LangGraph
        - Streamlit
        """
    )


# -------------------------------
# Upload Section
# -------------------------------
st.subheader("📤 Upload RFP Document")

uploaded_file = st.file_uploader(
    "Upload an RFP PDF file",
    type=["pdf"]
)


# -------------------------------
# Process Button
# -------------------------------
if uploaded_file is not None:

    st.info(f"📎 Selected file: **{uploaded_file.name}**")

    if st.button("🚀 Process RFP"):

        with st.spinner("Running Agentic AI workflow..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            try:
                response = requests.post(
                    BACKEND_URL,
                    files=files,
                    timeout=120
                )

                if response.status_code != 200:
                    st.error("❌ Backend Error")
                    st.code(response.text)

                else:
                    data = response.json()
                    st.session_state["rfp_result"] = data
                    st.success("✅ RFP processed successfully!")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Could not connect to backend.\n\n"
                    "Make sure FastAPI is running on port 8000."
                )

            except requests.exceptions.Timeout:
                st.error("❌ Backend request timed out.")

            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")


# -------------------------------
# Display Results
# -------------------------------
if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    st.markdown("---")
    st.header("📊 RFP Analysis Results")


    # ===============================
    # SALES SUMMARY
    # ===============================
    st.subheader("🧾 Sales Agent — RFP Qualification")

    sales = data.get("rfp_summary", {})

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("RFP ID", sales.get("rfp_id", "-"))
    col2.metric("Deadline", sales.get("deadline", "-"))
    col3.metric("Priority", sales.get("priority", "-"))
    col4.metric("Scope", sales.get("scope_summary", "-"))


    # ===============================
    # TECHNICAL OUTPUT
    # ===============================
    st.markdown("---")
    st.subheader("🛠️ Technical Agent — SKU Recommendations")

    technical = data.get("technical_summary", {})

    recommended_skus = technical.get("recommended_skus", [])

    if recommended_skus:

        df = pd.DataFrame({
            "Recommended SKU": recommended_skus
        })

        st.dataframe(df, use_container_width=True)

    else:

        st.info(
            "No SKU recommendations available."
        )


    # ===============================
    # PRICING OUTPUT
    # ===============================
    st.markdown("---")
    st.subheader("💰 Pricing Agent — Cost Breakdown")

    pricing = data.get("pricing_summary", {})

    sku_costs = pricing.get("sku_costs", {})

    if sku_costs:

        pricing_rows = []

        for sku, details in sku_costs.items():

            pricing_rows.append({
                "SKU": sku,
                "Unit Price": details["unit_price"],
                "Quantity": details["quantity"],
                "Total Cost": details["total"]
            })

        pricing_df = pd.DataFrame(pricing_rows)

        st.dataframe(pricing_df, use_container_width=True)

    else:
        st.info("No pricing data available.")


    # ===============================
    # TOTAL COST
    # ===============================
    total_cost = pricing.get("total_estimated_cost", 0)

    st.metric(
        "Total Estimated Cost",
        f"₹ {total_cost}"
    )


# -------------------------------
# Footer
# -------------------------------
st.markdown("---")

st.caption(
    "AURA — Agentic AI-based B2B RFP Response Automation System\n\n"
    "Capstone Project | Demonstrates Agentic AI, NLP, and Decision Support Systems"
)