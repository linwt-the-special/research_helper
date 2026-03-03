import streamlit as st
import os
import json
import time
import uuid
from main import app, save_state, load_state, get_all_sessions, SESSIONS_DIR, get_default_state
from agents.state import AgentState

st.set_page_config(page_title="科研助手", layout="wide")

# --- 自定义样式 ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 8px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
    .sota-dashboard { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .stCodeBlock { border-radius: 8px; }
    .scan-setting-box { background-color: #fff4e6; padding: 20px; border-radius: 10px; border: 1px solid #ffd8a8; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 状态初始化 ---
if "session_id" not in st.session_state: st.session_state.session_id = "default"
if "graph_state" not in st.session_state:
    st.session_state.graph_state = load_state(st.session_state.session_id) or get_default_state(st.session_state.session_id)

# --- 驱动函数 ---
def run_pipeline(updates=None):
    if updates: 
        if "input" in updates:
            st.session_state.graph_state["chat_history"].append({"role": "user", "content": updates["input"]})
        st.session_state.graph_state.update(updates)
    
    state = st.session_state.graph_state
    checkpoints = ["wait_keyword_confirm", "wait_paper_picking", "wait_plan_discussion", "wait_code_review", "end"]
    
    with st.status("🚀 专家团队正在协同作业...", expanded=True) as status:
        while state.get("next_node") not in checkpoints:
            curr = state.get("next_node", "coordinator")
            st.write(f"🔹 正在调度 `{curr.upper()}` 智能体...")
            for output in app.stream(state):
                for node_name, state_update in output.items():
                    state.update(state_update)
            save_state(state, st.session_state.session_id)
            time.sleep(0.2)
        status.update(label="✅ 专家已就绪", state="complete", expanded=False)
    st.rerun()

# --- 侧边栏：课题管理 ---
with st.sidebar:
    st.title("🔬 课题实验室")
    if st.button("➕ 开启新研究", use_container_width=True):
        st.session_state.session_id = f"res_{uuid.uuid4().hex[:6]}"
        st.session_state.graph_state = get_default_state(st.session_state.session_id)
        st.rerun()
    st.divider()
    st.subheader("📁 历史会话")
    sessions = get_all_sessions()
    for sid, title in sessions.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📄 {title[:12]}...", key=f"s_{sid}", use_container_width=True, 
                         type="primary" if sid == st.session_state.session_id else "secondary"):
                st.session_state.session_id = sid
                st.session_state.graph_state = load_state(sid)
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}"):
                file_path = os.path.join(SESSIONS_DIR, f"{sid}.json")
                if os.path.exists(file_path): os.remove(file_path)
                if st.session_state.session_id == sid:
                    st.session_state.session_id = "default"
                    st.session_state.graph_state = get_default_state("default")
                st.rerun()

# --- 布局规划 ---
col_chat, col_work = st.columns([1, 1.3])

# --- 左侧：核心对话舱 ---
with col_chat:
    st.header("💬 策略对话")
    chat_box = st.container(height=650)
    with chat_box:
        state = st.session_state.graph_state
        for msg in state.get("chat_history", []):
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                st.markdown(msg["content"])
        
        # 拦截点 1: 关键词确认
        if state.get("next_node") == "wait_keyword_confirm":
            with st.chat_message("assistant", avatar="🤖"):
                st.write("请确认我提炼的搜索关键词：")
                new_kw = st.text_input("Keywords:", value=state.get("refined_keywords", ""), label_visibility="collapsed")
                if st.button("确认并检索", type="primary"): 
                    run_pipeline({"refined_keywords": new_kw, "next_node": "scout"})

    # 全局对话入口 (只有在非扫描初始化阶段显示)
    if state.get("input") and state.get("next_node") not in ["wait_keyword_confirm", "wait_paper_picking"]:
        hint = "请输入指令或与团队讨论..."
        if prompt := st.chat_input(hint):
            run_pipeline({"input": prompt, "next_node": "coordinator"})

# --- 右侧：生产看板 ---
with col_work:
    st.header("🛠️ 深度生产区")
    state = st.session_state.graph_state
    curr = state.get("next_node")

    # 0. 初始扫描设置 (恢复时间区间控件)
    if not state.get("input"):
        st.markdown('<div class="scan-setting-box">', unsafe_allow_html=True)
        st.subheader("🔎 初始扫描设置 (Scan Setting)")
        with st.form("init_scan_form"):
            topic = st.text_input("请输入您的研究大方向 (如：电价预测模型):")
            years = st.select_slider(
                "论文发表时间区间:",
                options=[str(y) for y in range(2010, 2027)],
                value=("2023", "2026")
            )
            if st.form_submit_button("🚀 开启全网影响力扫描", use_container_width=True):
                if topic:
                    run_pipeline({
                        "input": topic, 
                        "year_range": f"{years[0]}-{years[1]}",
                        "next_node": "coordinator"
                    })
        st.markdown('</div>', unsafe_allow_html=True)

    # 1. 文献池 (CP2)
    if curr == "wait_paper_picking" or (state.get("papers") and not state.get("analysis_report")):
        st.subheader("📚 影响力文献池")
        selected = []
        for i, p in enumerate(state["papers"]):
            with st.expander(f"⭐ {p.get('score', 0)} | {p['title']}"):
                st.write(f"**引用**: {p.get('citations')} | **年份**: {p.get('published')}")
                st.write(p.get("summary"))
                if st.checkbox("选择分析", key=f"sel_{i}"): selected.append(i)
        if curr == "wait_paper_picking" and st.button("确认并进行深度对比", type="primary", use_container_width=True):
            run_pipeline({"selected_paper_ids": selected, "next_node": "analyst"})

    # 2. SOTA 仪表盘 (Analyst 产出参考信息)
    if state.get("sota_table"):
        st.markdown('<div class="sota-dashboard">', unsafe_allow_html=True)
        st.subheader("📊 SOTA 性能对比表 (参考)")
        st.markdown(state["sota_table"])
        st.markdown('</div>', unsafe_allow_html=True)
        if state.get("analysis_report"):
            with st.expander("📄 查看文献调研参考报告"):
                st.markdown(state["analysis_report"])

    # 3. 研究计划编辑器 (讨论完成后人工确认)
    if curr == "wait_plan_discussion" or state.get("research_plan"):
        st.divider()
        st.subheader("📝 正式研究计划 (Research Plan)")
        plan_val = state.get("research_plan") or "请通过左侧对话讨论确定思路，或在此直接输入..."
        edited_plan = st.text_area("Editor", value=plan_val, height=400, label_visibility="collapsed")
        if st.button("✅ 确认计划并指派复现", type="primary", use_container_width=True):
            run_pipeline({"research_plan": edited_plan, "next_node": "coder"})

    # 4. 代码执行区
    if state.get("code"):
        st.subheader("💻 代码落地与执行")
        st.code(state["code"], language="python")
        if state.get("console_output"):
            with st.expander("📟 执行日志", expanded=True): st.code(state["console_output"])
        if curr == "wait_code_review":
            if st.button("🚀 授权执行实验", type="primary", use_container_width=True):
                run_pipeline({"next_node": "executor"})

    # 底部执行日志
    with st.expander("🛠️ 系统内部日志 (仅供调试)"):
        for log in state.get("history", []):
            st.caption(log)
