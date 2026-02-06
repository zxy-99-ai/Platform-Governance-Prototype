import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Platform Governance Prototype", layout="wide")

# --- 1. 模拟真实的 4,200 个商家分布 ---
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 4200
    regions = ['Japan', 'Taiwan', 'South Korea', 'Singapore', 'Thailand', 'Vietnam', 'Europe', 'Americas']
    bu = ['Attractions', 'Mobility']
    # 匹配你 Excel 中的 Growth Segment
    segments = ['C-1 (Champion)', 'C-2 (High Session)', 'C-3 (High CVR)', 'C-4 (High Growth)', 'D (Standard)']
    
    data = {
        'Activity_ID': range(10000, 10000 + n),
        'Region': np.random.choice(regions, n),
        'Vertical': np.random.choice(bu, n),
        'Segment': np.random.choice(segments, n, p=[0.05, 0.1, 0.05, 0.1, 0.7]),
        'Gross_Sales': np.random.lognormal(10, 1.5, n),
        # 对应你 scoring mechanism 中的指标
        'Instant_Confirm_Actual': np.random.uniform(0.6, 1.0, n),
        'Free_Cancel_Actual': np.random.uniform(0.4, 1.0, n),
        'Same_Day_Avail_Actual': np.random.uniform(0.3, 1.0, n),
        'Bad_Review_Rate': np.random.beta(2, 50, n),
        'Fulfillment_Failure': np.random.beta(1, 100, n)
    }
    return pd.DataFrame(data)

df = load_data()

# --- 2. 侧边栏：治理杠杆 (Governance Levers) ---
st.sidebar.title("🛠 平台商家治理策略中心")
st.sidebar.info("根据Program逻辑，调整参数以观察生态分层变化")

# 权重设置 (基于 scoring mechanism.csv)
st.sidebar.subheader("1. 绩效评分权重 (SS Total)")
w_confirm = st.sidebar.slider("即时确认 (Instant Confirm)", 0.0, 2.0, 1.0)
w_cancel = st.sidebar.slider("免费取消 (Free Cancel)", 0.0, 2.0, 1.0)
w_avail = st.sidebar.slider("当天可订 (Same Day Avail)", 0.0, 2.0, 1.5)

# 阈值设置 (基于 MVP logic overview.csv)
st.sidebar.subheader("2. 权益解锁门槛")
l1_target = st.sidebar.number_input("L1 Unlock (Basic) 门槛分数", value=15)
l2_target = st.sidebar.number_input("L2 Unlock (Premium) 门槛分数", value=45)

# --- 3. 治理引擎计算 ---
def run_governance(data):
    d = data.copy()
    # 模拟分数计算逻辑
    d['Performance_Points'] = (
        (d['Instant_Confirm_Actual'] * 10 * w_confirm) +
        (d['Free_Cancel_Actual'] * 10 * w_cancel) +
        (d['Same_Day_Avail_Actual'] * 15 * w_avail)
    )
    
    # 合规判定
    d['Is_Compliant'] = d['Fulfillment_Failure'] < 0.03 # 假设红线为3%
    
    def define_tier(row):
        if not row['Is_Compliant']: return "🔴 Restricted"
        if row['Performance_Points'] >= l2_target: return "🥇 L2 (Premium)"
        if row['Performance_Points'] >= l1_target: return "🥈 L1 (Basic)"
        return "🥉 Standard"
    
    d['Final_Tier'] = d.apply(define_tier, axis=1)
    return d

final_df = run_governance(df)

# --- 4. 仪表盘主界面 ---
st.title("🛡️ Ecosystem Governance Architecture")
st.markdown("该原型展示了如何将平台的业务标准转化为可自动运行的商家治理系统。")

# 核心指标看板
k1, k2, k3, k4 = st.columns(4)
k1.metric("总商家数", len(final_df))
k2.metric("L2 高级伙伴", len(final_df[final_df['Final_Tier'] == "🥇 L2 (Premium)"]))
k3.metric("受限商家", len(final_df[final_df['Final_Tier'] == "🔴 Restricted"]))
k4.metric("平均性能分", round(final_df['Performance_Points'].mean(), 1))

st.divider()

# 图表展现
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 商家分层分布 (按 Growth Segment)")
    fig = px.histogram(final_df, x="Segment", color="Final_Tier", barmode="group",
                       category_orders={"Segment": ['C-1 (Champion)', 'C-2 (High Session)', 'C-3 (High CVR)', 'C-4 (High Growth)', 'D (Standard)']})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🎯 区域覆盖占比")
    fig_pie = px.pie(final_df, names='Region', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# 交互式列表
st.subheader("🔍 商家治理详情预览 (Top 50)")
st.dataframe(final_df[['Activity_ID', 'Region', 'Segment', 'Performance_Points', 'Final_Tier']].head(50))