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

/* Background */
.main {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e5e7eb;
}

/* Hero Title */
.hero {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Glass Cards */
.glass {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    color: white;
    font-weight: 600;
    border: none;
    padding: 10px 18px;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(139,92,246,0.4);
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HERO
# -------------------------------
st.markdown('<div class="hero">AURA — Agentic RFP Intelligence</div>', unsafe_allow_html=True)
st.caption("AI-powered RFP automation platform")

st.markdown("---")

# -------------------------------
# Backend URL
# -------------------------------
BACKEND_URL = "http://localhost:8000/process-rfp"

# ===============================
# 🧭 CONTROL PANEL
# ===============================
st.markdown("## ⚙️ Control Panel")

col1, col2, col3 = st.columns(3)

# -------- Product KB --------
with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📦 Product KB")

    catalogue_file = st.file_uploader("Upload Catalogue", type=["pdf"])

    if catalogue_file is not None:
        st.info(f"{catalogue_file.name}")

        if st.button("Process Catalogue"):
            with st.spinner("Processing catalogue..."):
                files = {
                    "file": (
                        catalogue_file.name,
                        catalogue_file.getvalue(),
                        "application/pdf"
                    )
                }

                try:
                    response = requests.post(
                        "http://localhost:8000/upload-product-catalogue",
                        files=files
                    )

                    if response.status_code == 200:
                        st.balloons()
                        st.success("Catalogue processed!")
                    else:
                        st.error("Failed")
                        st.code(response.text)

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# -------- Pricing KB --------
with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("💰 Pricing KB")

    pricing_file = st.file_uploader("Upload Pricing", type=["pdf"], key="pricing")

    if pricing_file is not None:
        st.info(f"{pricing_file.name}")

        if st.button("Process Pricing"):
            with st.spinner("Processing pricing..."):
                files = {
                    "file": (
                        pricing_file.name,
                        pricing_file.getvalue(),
                        "application/pdf"
                    )
                }

                try:
                    response = requests.post(
                        "http://localhost:8000/upload-pricing",
                        files=files
                    )

                    if response.status_code == 200:
                        res = response.json()

                        inserted = res.get("entries_added", 0)

                        if inserted == 0:
                            st.warning("⚠️ No pricing data extracted. Check PDF format.")
                        else:
                            st.success(f"✅ Pricing processed! {inserted} entries added.")
                    else:
                        st.error("Failed")
                        st.code(response.text)

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# -------- RFP Upload --------
with col3:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📤 RFP Processing")

    uploaded_file = st.file_uploader("Upload RFP", type=["pdf"])

    if uploaded_file is not None:
        st.info(f"{uploaded_file.name}")

        if st.button("Run AURA"):
            with st.spinner("Running AI workflow..."):
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

                    if response.status_code == 200:
                        st.session_state["rfp_result"] = response.json()
                        st.balloons()
                        st.success("RFP processed successfully!")
                    else:
                        st.error("Backend Error")
                        st.code(response.text)

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# 📊 MAIN DASHBOARD
# ===============================
st.markdown("## 📊 Dashboard")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    sales = data.get("rfp_summary", {})
    technical = data.get("technical_summary", {})
    pricing = data.get("pricing_summary", {})

    total_cost = pricing.get("total_estimated_cost", 0)

    # KPI ROW
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("RFP ID", sales.get("rfp_id", "-"))
    k2.metric("Deadline", sales.get("deadline", "-"))
    k3.metric("Priority", sales.get("priority", "-"))
    k4.metric("Total Cost", f"₹ {total_cost:,.0f}")

    # CHARTS
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 💰 Cost Breakdown")
        df_price = pd.DataFrame(pricing.get("pricing_details", []))

        if not df_price.empty and "total_price" in df_price.columns:
            st.bar_chart(df_price.set_index(df_price.columns[0])["total_price"])

    with c2:
        st.markdown("### 🛠 SKU Recommendations")
        skus = technical.get("recommended_skus", [])

        df_sku = pd.DataFrame({"SKU": skus})

        if not df_sku.empty:
            st.bar_chart(df_sku.value_counts())

# ===============================
# ⚙️ DETAILED INSIGHTS
# ===============================
st.markdown("---")
st.markdown("## 🔍 Detailed Insights")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    tab1, tab2, tab3 = st.tabs(["Overview", "Technical", "Pricing"])

    with tab1:
        st.json(data.get("rfp_summary", {}))

    with tab2:
        tech_data = data.get("technical_summary", {}).get("recommended_skus", [])
        st.dataframe(pd.DataFrame(tech_data))

    with tab3:
        pricing_data = data.get("pricing_summary", {}).get("pricing_details", [])
        st.dataframe(pd.DataFrame(pricing_data))

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("AURA — AI-driven RFP Intelligence Platform")