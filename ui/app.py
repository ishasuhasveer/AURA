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
.metric-card {
    background: rgba(255,255,255,0.04);
    padding: 10px;
    border-radius: 10px;
}
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    color: white;
}

/* SKU Cards */
.sku-card {
    background: rgba(255,255,255,0.05);
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}
.sku-title {
    font-size: 18px;
    font-weight: 600;
}
.sku-score {
    font-size: 14px;
    color: #9ca3af;
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

with col2:
    st.markdown("### 💰 Pricing KB")
    file = st.file_uploader("Upload Pricing", type=["pdf"], key="pricing")

    if file and st.button("Process Pricing"):
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        res = requests.post("http://localhost:8000/upload-pricing", files=files)
        st.success(res.json())

with col3:
    st.markdown("### 📤 RFP Processing")
    file = st.file_uploader("Upload RFP", type=["pdf"], key="rfp")

    if file and st.button("Run AURA"):
        with st.spinner("Processing RFP..."):
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            res = requests.post(BACKEND_URL, files=files)

        if res.status_code == 200:
            st.session_state["rfp_result"] = res.json()
            st.success("RFP processed successfully!")
        else:
            st.error(res.text)

# ===============================
# HELPER: EXTRACT SKU DATA
# ===============================

def extract_skus(data):
    top = data.get("top_sku_recommendations", [])
    scores = data.get("spec_match_scores", {})

    if top:
        skus = [item.get("sku_config_id") for item in top]
        return skus, scores

    # fallback (rare)
    decision = data.get("decision_table", [])
    sku_scores = {}

    for req in decision:
        for match in req.get("top_matches", []):
            sid = match.get("sku_config_id")
            score = match.get("match_percent", 0)

            if not sid:
                continue

            if sid not in sku_scores or sku_scores[sid] < score:
                sku_scores[sid] = score

    sorted_skus = sorted(sku_scores, key=sku_scores.get, reverse=True)

    return sorted_skus[:5], sku_scores

# ===============================
# DASHBOARD
# ===============================
st.markdown("## 📊 Dashboard")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    status = data.get("status", "success")

    if status != "success":
        st.error(f"⚠️ Status: {status}")
    else:
        st.success("✅ Processing Successful")
    # ---------------- ERROR + AI OUTPUT ----------------
    error = data.get("error")
    suggested = data.get("suggested_skus", [])
    analysis = data.get("analysis")
    recommendation = data.get("recommendation")

    if error:
        st.warning(f"⚠️ {error}")

    if analysis:
        st.subheader("📊 Gap Analysis")

        colA, colB, colC = st.columns(3)

        colA.metric("Required Size", analysis.get("required_size") or "N/A")
        colB.metric("Max Available", analysis.get("max_available_size") or "N/A")
        colC.metric("Gap Ratio", analysis.get("gap_ratio") or "N/A")

        if analysis.get("insight"):
            st.warning(analysis["insight"])

    if suggested:
        st.subheader("🤖 AI Suggested SKUs")

        for s in suggested:
            if isinstance(s, dict):
                st.write(f"• {s.get('sku_config_id')} (Size: {s.get('size', 'N/A')} sqmm)")
            else:
                st.write(f"• {s}")

    if recommendation:
        st.success(f"💡 {recommendation}")

    # ---------------- CORE DATA ----------------
    sales = data.get("rfp_summary", {})
    pricing = data.get("pricing_summary", {})

    skus, scores = extract_skus(data)

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

    if not df_price.empty:
        df_price = df_price[["sku_config_id", "total_price"]]
        df_price = df_price.set_index("sku_config_id")
        st.bar_chart(df_price)
        st.dataframe(df_price.reset_index(), use_container_width=True)

    else:
        st.info("No pricing data available")

    # ---------------- SKU RECOMMENDATIONS ----------------
    st.markdown("### 🛠 Top SKU Recommendations")

    if skus:
        for i, sku in enumerate(skus):
            score = round(scores.get(sku, 0), 2) if scores else 0

            st.markdown(f"""
            <div class="sku-card">
                <div class="sku-title">#{i + 1} — {sku}</div>
                <div class="sku-score">Match Score: {score}%</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(min(score / 100, 1.0))

    else:
        st.warning("No exact SKUs matched")

# ===============================
# DETAILS
# ===============================
st.markdown("---")
st.markdown("## 🔍 Detailed Insights")

if "rfp_result" in st.session_state:

    data = st.session_state["rfp_result"]

    decision_table = data.get("decision_table", [])

    pricing_data = data.get("pricing_summary", {}).get("pricing_details", [])

    tab1, tab2, tab3 = st.tabs(["Overview", "Technical", "Pricing"])

    # -------- OVERVIEW --------
    with tab1:
        st.json(data.get("rfp_summary", {}))

    # -------- TECHNICAL --------
    with tab2:
        if decision_table:
            for req in decision_table:

                st.markdown("### 🔹 Requirement Analysis")

                for sku_block in req.get("top_matches", []):

                    score = sku_block['match_percent']

                    st.markdown(f"**{sku_block.get('sku_config_id')}** — {score}% match")
                    st.progress(score / 100)

                    df = pd.DataFrame(sku_block["table"])
                    st.dataframe(df, use_container_width=True)

        else:
            st.warning("No technical comparison available")

    # -------- PRICING --------
    with tab3:
        if pricing_data:

            df = pd.DataFrame(pricing_data)
            df = df.sort_values(by="total_price", ascending=False)

            st.dataframe(df, use_container_width=True)

            if not df.empty:
                top = df.iloc[0]
                st.success(f"💡 Recommended SKU: {top['sku_config_id']} (₹ {top['total_price']:,.0f})")

        else:
            st.warning("No pricing data available")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("AURA — AI-driven RFP Intelligence Platform")