import streamlit as st
import requests
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AURA — Agentic RFP Assistant",
    layout="wide"
)

# -------------------------------
# GLOBAL STYLING
# -------------------------------
st.markdown("""
<style>
.main {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e5e7eb;
}
.hero {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.glass {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown('<div class="hero">AURA — Agentic RFP Intelligence</div>', unsafe_allow_html=True)
st.caption("AI-powered RFP automation platform")
st.markdown("---")

BACKEND_URL = "http://localhost:8000/process-rfp"

# ===============================
# CONTROL PANEL
# ===============================
st.markdown("## ⚙️ Control Panel")
col1, col2, col3 = st.columns(3)

# -------- PRODUCT KB --------
with col1:
    st.markdown("### 📦 Product KB")
    file = st.file_uploader("Upload Catalogue", type=["pdf"])

    if file and st.button("Process Catalogue"):
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        res = requests.post("http://localhost:8000/upload-product-catalogue", files=files)
        if res.status_code == 200:
            st.success("Catalogue processed")
        else:
            st.error(res.text)

# -------- PRICING KB --------
with col2:
    st.markdown("### 💰 Pricing KB")
    file = st.file_uploader("Upload Pricing", type=["pdf"], key="pricing")

    if file and st.button("Process Pricing"):
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        res = requests.post("http://localhost:8000/upload-pricing", files=files)
        st.success(res.json())

# -------- RFP --------
with col3:
    st.markdown("### 📤 RFP Processing")
    file = st.file_uploader("Upload RFP", type=["pdf"], key="rfp")

    if file and st.button("Run AURA"):
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        res = requests.post(BACKEND_URL, files=files)

        if res.status_code == 200:
            st.session_state["rfp_result"] = res.json()
            st.success("RFP processed successfully!")
        else:
            st.error(res.text)

# ===============================
# DASHBOARD
# ===============================
st.markdown("## 📊 Dashboard")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    sales = data.get("rfp_summary", {})
    technical = data.get("technical_summary", {})
    pricing = data.get("pricing_summary", {})

    total_cost = pricing.get("total_estimated_cost", 0) or 0

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("RFP ID", sales.get("rfp_id", "-"))
    k2.metric("Deadline", str(sales.get("deadline", "-")))
    k3.metric("Priority", sales.get("priority", "-"))
    k4.metric("Total Cost", f"₹ {total_cost:,.0f}")

    # ---------------- COST CHART ----------------
    st.markdown("### 💰 Cost Breakdown")

    pricing_details = pricing.get("pricing_details", [])
    df_price = pd.DataFrame(pricing_details)

    if not df_price.empty and "total_price" in df_price.columns:
        df_price = df_price[["sku_id", "total_price"]]
        df_price = df_price.set_index("sku_id")
        st.bar_chart(df_price)

    else:
        st.info("No pricing data available")

    # ---------------- SKU CHART ----------------
    st.markdown("### 🛠 SKU Recommendations")

    skus = technical.get("recommended_skus", [])

    if skus:
        df_sku = pd.DataFrame({"SKU": skus})
        chart_data = df_sku["SKU"].value_counts().reset_index()
        chart_data.columns = ["SKU", "Count"]

        st.bar_chart(chart_data.set_index("SKU"))
    else:
        st.info("No SKUs recommended")

# ===============================
# DETAILS
# ===============================
st.markdown("---")
st.markdown("## 🔍 Detailed Insights")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    tab1, tab2, tab3 = st.tabs(["Overview", "Technical", "Pricing"])

    with tab1:
        st.json(data.get("rfp_summary", {}))

    with tab2:
        tech = data.get("technical_summary", {}).get("recommended_skus", [])
        st.dataframe(pd.DataFrame({"SKU": tech}))

    with tab3:
        pricing_data = data.get("pricing_summary", {}).get("pricing_details", [])
        st.dataframe(pd.DataFrame(pricing_data))

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("AURA — AI-driven RFP Intelligence Platform")