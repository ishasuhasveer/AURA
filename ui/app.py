import streamlit as st
import requests
import pandas as pd
import altair as alt


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
BACKEND_URL = "http://localhost:8000/process-rfp"


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

    st.markdown("---")

    if st.button("🔄 Reset Analysis"):
        st.session_state.clear()
        st.rerun()


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
    st.header("📊 RFP Analysis Dashboard")

    sales = data.get("rfp_summary", {})
    technical = data.get("technical_summary", {})
    pricing = data.get("pricing_summary", {})

    recommended_skus_data = technical.get("recommended_skus", [])

    # Extract only SKU IDs for UI
    recommended_skus = [
        sku["sku_id"] if isinstance(sku, dict) else sku
        for sku in recommended_skus_data
    ]
    spec_scores = {
        sku["sku_id"]: sku.get("spec_match_percent", 0)
        for sku in recommended_skus_data
    }
    pricing_details = pricing.get("pricing_details", [])

    total_cost = pricing.get("total_estimated_cost", 0)

    # -------------------------------
    # Tabs Layout
    # -------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Overview",
            "🛠 Technical Analysis",
            "💰 Pricing Insights",
            "⚙️ Agent Workflow"
        ]
    )

    # ===============================
    # OVERVIEW TAB
    # ===============================
    with tab1:

        st.subheader("📄 RFP Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("RFP ID", sales.get("rfp_id", "-"))
        col2.metric("Deadline", sales.get("deadline", "-"))
        col3.metric("Priority", sales.get("priority", "-"))

        st.markdown("### Scope Summary")

        st.info(
            sales.get("scope_summary", "No scope summary available.")
        )

        st.markdown("### Estimated Bid Value")

        st.metric(
            "Total Estimated Cost",
            f"₹ {total_cost:,.0f}"
        )


    # ===============================
    # TECHNICAL TAB
    # ===============================
    with tab2:

        st.subheader("🛠 SKU Recommendations")

        if recommended_skus:

            df = pd.DataFrame({
                "Recommended SKU": recommended_skus
            })

            st.dataframe(df, use_container_width=True)

            # -----------------------
            # Spec Match Chart
            # -----------------------
            if spec_scores:

                st.markdown("### Spec Match Comparison")

                chart_df = pd.DataFrame({
                    "SKU": list(spec_scores.keys()),
                    "Spec Match %": list(spec_scores.values())
                })

                chart = alt.Chart(chart_df).mark_bar().encode(
                    x="SKU",
                    y="Spec Match %",
                    tooltip=["SKU", "Spec Match %"]
                ).properties(height=350)

                st.altair_chart(chart, use_container_width=True)

            # -----------------------
            # Interactive SKU Viewer
            # -----------------------
            selected_sku = st.selectbox(
                "Inspect SKU",
                recommended_skus
            )

            if selected_sku:
                score = spec_scores.get(selected_sku, "N/A")

                st.info(
                    f"SKU: {selected_sku} | Spec Match: {score}%"
                )

        else:

            st.info("No SKU recommendations available.")


    # ===============================
    # PRICING TAB
    # ===============================
    with tab3:

        st.subheader("💰 Pricing Breakdown")

        if pricing_details:

            pricing_rows = []

            for item in pricing_details:
                pricing_rows.append({
                    "SKU": item.get("sku_id"),
                    "Unit Price": item.get("unit_price", 0),
                    "Quantity": item.get("quantity", 0),
                    "Total Cost": item.get("total_price", 0)
                })
            pricing_df = pd.DataFrame(pricing_rows)

            st.dataframe(pricing_df, use_container_width=True)

            st.markdown("### Cost Comparison")

            chart = alt.Chart(pricing_df).mark_bar().encode(
                x="SKU",
                y="Total Cost",
                tooltip=["SKU", "Total Cost"]
            ).properties(height=350)

            st.altair_chart(chart, use_container_width=True)

        else:

            st.info("No pricing data available.")


    # ===============================
    # AGENT WORKFLOW TAB
    # ===============================
    with tab4:

        st.subheader("⚙️ Agent Execution Pipeline")

        workflow = [
            ("Sales Agent", "RFP Qualification"),
            ("Document Intelligence", "Requirement Extraction"),
            ("Technical Agent", "SKU Matching"),
            ("Pricing Agent", "Cost Estimation"),
            ("Main Orchestrator", "Response Consolidation")
        ]

        for agent, task in workflow:

            st.success(f"{agent} → {task}")


# -------------------------------
# Footer
# -------------------------------
st.markdown("---")

st.caption(
    "AURA — Agentic AI-based B2B RFP Response Automation System\n\n"
    "Capstone Project | Demonstrates Agentic AI, NLP, and Decision Support Systems"
)