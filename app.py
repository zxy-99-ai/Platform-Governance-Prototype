import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. 页面配置与主题 ---
st.set_page_config(page_title="Ecosystem Governance & Merchant Audit", layout="wide")

# 自定义 CSS 提升 UI 质感
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 模拟数据集 (精准对齐 C-1/C-2/C-3/D 逻辑) ---
@st.cache_data
def load_klook_aligned_data():
    np.random.seed(42)
    n = 4500
    regions = ['APAC', 'EMEA', 'AMER', 'SEA', 'Greater China']
    categories = ['Experiences', 'Transportation', 'Staycation']
    # 恢复 C-1, C-2, C-3, D 命名
    segments = ['C-1 (Champion)', 'C-2 (High Session)', 'C-3 (High CVR)', 'D (Standard)']
    
    data = {
        'Merchant_ID': [f"M_{i:05d}" for i in range(n)],
        'Region': np.random.choice(regions, n),
        'Category': np.random.choice(categories, n),
        'Growth_Segment': np.random.choice(segments, n, p=[0.08, 0.15, 0.07, 0.70]),
        'Monthly_GMV': np.random.lognormal(11, 1.4, n), # 模拟长尾分布
        'SLA_Rate': np.random.uniform(0.5, 1.0, n),
        'User_Rating': np.random.uniform(3.5, 5.0, n),
        'Cancellation_Rate': np.random.beta(1, 20, n),
        'Fulfillment_Failure': np.random.beta(1, 100, n)
    }
    return pd.DataFrame(data)

df_raw = load_klook_aligned_data()

# --- 3. 侧边栏：治理杠杆 ---
with st.sidebar:
    st.title("🛡️ Governance Levers")
    st.write("Simulate policy impact on C-1/C-2/C-3/D merchants.")
    
    st.subheader("⚙️ Scoring Weights")
    w_sla = st.slider("SLA Adherence Weight", 0.0, 2.0, 1.2)
    w_rating = st.slider("Customer Rating Weight", 0.0, 2.0, 1.0)
    w_ops = st.slider("Ops Reliability Weight", 0.0, 2.0, 0.8)
    
    st.subheader("🔓 Unlock Thresholds")
    l1_threshold = st.number_input("L1 Premium Unlock", value=45)
    l2_threshold = st.number_input("L2 Basic Unlock", value=20)
    
    st.subheader("🚨 Compliance Guardrail")
    max_failure = st.slider("Max Failure Rate (%)", 0.0, 5.0, 1.5) / 100

# --- 4. 治理逻辑引擎 ---
def apply_governance(data):
    d = data.copy()
    # 模拟分数计算 (0-100)
    d['Governance_Score'] = (
        (d['SLA_Rate'] * 40 * w_sla) + 
        ((d['User_Rating']-3.5)/1.5 * 30 * w_rating) + 
        ((1 - d['Cancellation_Rate']) * 30 * w_ops)
    )
    
    # 合规判定
    d['Compliant'] = d['Fulfillment_Failure'] <= max_failure
    
    def get_tier(row):
        if not row['Compliant']: return "🔴 Restricted (High Risk)"
        if row['Governance_Score'] >= l1_threshold: return "🥇 L2 (Premium Benefits)"
        if row['Governance_Score'] >= l2_threshold: return "🥈 L1 (Basic Benefits)"
        return "🥉 Standard"
    
    d['Final_Status'] = d.apply(get_tier, axis=1)
    
    # ROI 影响模拟 (T1 提升, Restricted 损失)
    d['Impacted_GMV'] = d['Monthly_GMV']
    d.loc[d['Final_Status'] == "🥇 L2 (Premium Benefits)", 'Impacted_GMV'] *= 1.15
    d.loc[d['Final_Status'] == "🔴 Restricted (High Risk)", 'Impacted_GMV'] *= 0.4
    return d

df_final = apply_governance(df_raw)

# --- 5. 主页面布局 ---
st.title("🌐 Platform Governance & Merchant Audit")
st.markdown("Automated Tiering for **C-1 (Champions)** to **D (Standard)** Supply Chains.")

# A. 顶层 KPI
m1, m2, m3, m4 = st.columns(4)
gmv_delta = (df_final['Impacted_GMV'].sum() - df_final['Monthly_GMV'].sum()) / df_final['Monthly_GMV'].sum() * 100

with m1: st.metric("Global Merchants", len(df_final))
with m2: st.metric("L2 Premium Unlock", len(df_final[df_final['Final_Status'].str.contains("L2")]))
with m3: st.metric("Est. GMV Impact", f"{gmv_delta:.2f}%")
with m4: st.metric("Health Rate", f"{df_final['Compliant'].mean()*100:.1f}%")

st.divider()

# B. 核心分析
tab1, tab2 = st.tabs(["📈 Tiering Distribution", "🔍 Top 50 Merchant Audit"])

with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Tiering Logic across C-1 to D Segments")
        fig = px.histogram(df_final, x="Growth_Segment", color="Final_Status", barmode="group",
                           category_orders={"Growth_Segment": ['C-1 (Champion)', 'C-2 (High Session)', 'C-3 (High CVR)', 'D (Standard)']},
                           color_discrete_map={
                               "🥇 L2 (Premium Benefits)": "#FFD700", "🥈 L1 (Basic Benefits)": "#C0C0C0",
                               "🥉 Standard": "#A9A9A9", "🔴 Restricted (High Risk)": "#FF4B4B"
                           })
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Score vs Risk Mapping")
        fig_scatter = px.scatter(df_final.sample(1000), x="Governance_Score", y="Fulfillment_Failure", 
                                 color="Final_Status", hover_data=['Merchant_ID'])
        fig_scatter.add_hline(y=max_failure, line_dash="dash", line_color="red")
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("💎 Top 50 Merchants by GMV (Strategic Audit)")
    st.markdown("These are your most critical assets. High-GMV merchants in **RED** require immediate attention.")
    
    # 锁定 Top 50
    top_50 = df_final.sort_values('Monthly_GMV', ascending=False).head(50)
    
    # 格式化表格显示
    st.dataframe(top_50[['Merchant_ID', 'Region', 'Growth_Segment', 'Monthly_GMV', 'Governance_Score', 'Final_Status']].style.applymap(
        lambda x: 'background-color: #ffcccc' if x == "🔴 Restricted (High Risk)" else '', subset=['Final_Status']
    ))
    
    # 搜索功能
    search_id = st.text_input("Enter Merchant ID to view detailed diagnostics (e.g., M_00001):")
    if search_id:
        res = df_final[df_final['Merchant_ID'] == search_id]
        if not res.empty:
            st.json(res.iloc[0].to_dict())
        else:
            st.error("Merchant ID not found.")

# --- 6. 底部文档 ---
with st.expander("📝 Implementation Methodology"):
    st.write("""
    - **C-1/C-2/C-3 Logic**: Based on historical session and CVR benchmarks.
    - **Governance Tiering**: L2 is unlocked for merchants meeting high Performance + Compliance bars.
    - **Actionability**: This dashboard enables BD teams to identify top-tier merchants penalized by risk guardrails for corrective action.
    """)
