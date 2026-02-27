import streamlit as st
import pandas as pd

# --- 初始化系统存储 (Session State Initialization) ---
# 治理逻辑：如果系统里没数据，就加载初始架构；如果有，就沿用你的实时调整
if 'quests' not in st.session_state:
    st.session_state.quests = pd.DataFrame([
        {"Quest": "完成 AI 治理引擎逻辑闭环", "Category": "🔴 Main", "Status": False, "Energy": "High"},
        {"Quest": "16个月宝宝日常副本", "Category": "🔵 Daily", "Status": False, "Energy": "Constant"},
        {"Quest": "Stream C 英文表达练习", "Category": "🟡 Leveling", "Status": False, "Energy": "Mid"}
    ])

if 'skill_levels' not in st.session_state:
    st.session_state.skill_levels = {"Governance": 45, "IP": 100, "Articulation": 25}

# --- 页面配置 ---
st.set_page_config(page_title="OneStone Commander", layout="wide")
st.title("🛡️ OneStone 交互式控制塔")

# --- 1. 资源实时审计 (Resource HUD) ---
with st.sidebar:
    st.header("📊 资源实时分配")
    hp = st.slider("HP (物理续航)", 0, 100, 70)
    mp = st.slider("MP (逻辑带宽)", 0, 100, 50)
    
    st.divider()
    st.subheader("🌲 技能树实时微调")
    # 动态调整技能树进度
    st.session_state.skill_levels["Governance"] = st.number_input("Governance (A)", 0, 100, st.session_state.skill_levels["Governance"])
    st.session_state.skill_levels["Articulation"] = st.number_input("Articulation (C)", 0, 100, st.session_state.skill_levels["Articulation"])

# --- 2. 动态任务编辑器 (The Quest Editor) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📜 动态任务日志 (Quest Log)")
    st.caption("💡 你可以直接在下表中点击编辑、新增或勾选完成。")
    
    # 核心组件：可编辑数据表
    edited_df = st.data_editor(
        st.session_state.quests,
        num_rows="dynamic",  # 允许你手动增加行
        use_container_width=True,
        key="quest_editor"
    )
    # 保存更改
    st.session_state.quests = edited_df

with col2:
    st.subheader("📈 技能树状态")
    for skill, val in st.session_state.skill_levels.items():
        st.write(f"**{skill}**")
        st.progress(val / 100)

# --- 3. 自动化决策辅助 (Governance Logic) ---
st.divider()
if st.button("运行能效审计 (Run Audit)"):
    # 逻辑逻辑：计算未完成的高耗能任务
    high_energy_tasks = st.session_state.quests[
        (st.session_state.quests['Status'] == False) & (st.session_state.quests['Energy'] == 'High')
    ]
    if mp < 40 and not high_energy_tasks.empty:
        st.error(f"⚠️ 警告：当前 MP ({mp}) 极低，建议暂停主线任务：{high_energy_tasks['Quest'].iloc[0]}")
    else:
        st.success("✅ 当前资源配比合理，逻辑带宽足以支撑现有任务。")
