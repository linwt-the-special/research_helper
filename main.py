import json
import os
import uuid
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.coordinator import CoordinatorAgent
from agents.scout import ScoutAgent
from agents.analyst import AnalystAgent
from agents.coder import CoderAgent
from agents.critic import CriticAgent
from agents.creative import CreativeAgent
from agents.summarizer import summarizer
from utils.executor import run_python_code_safe

coordinator = CoordinatorAgent()
scout = ScoutAgent()
analyst = AnalystAgent()
coder = CoderAgent()
critic = CriticAgent()
creative = CreativeAgent()

SESSIONS_DIR = "data/sessions"
MAX_STEPS = 50

def get_default_state(session_id: str = "default") -> AgentState:
    """核心加固：定义标准状态模板，确保所有字段始终存在"""
    return {
        "chat_history": [],
        "input": "", 
        "year_range": "2023-2026", 
        "refined_keywords": "", 
        "selected_paper_ids": [], 
        "papers": [], 
        "analysis_report": "", 
        "sota_table": "", 
        "research_plan": "", 
        "ideas": [], 
        "code": "", 
        "errors": [], 
        "console_output": "", 
        "feedback": "",
        "history": [], 
        "next_node": "coordinator", 
        "session_id": session_id
    }

def get_state_file(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def save_state(state: AgentState, session_id: str = "default"):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    history = state.get("history", [])
    if len(history) > 15:
        to_summarize = history[:-5]
        new_summary = summarizer.execute(to_summarize)
        old_context = state.get("research_context", "")
        state["research_context"] = f"{old_context}\n\n【前期回顾】:\n{new_summary}"
        state["history"] = history[-5:]
    state_file = get_state_file(session_id)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(dict(state), f, ensure_ascii=False, indent=2)

def load_state(session_id: str = "default") -> AgentState:
    """加载并自动对齐字段"""
    state_file = get_state_file(session_id)
    default_state = get_default_state(session_id)
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # 将加载的数据合并到模板中，确保缺失字段被补全
                default_state.update(loaded)
                return default_state
        except: return default_state
    return None

def get_all_sessions() -> Dict[str, str]:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    sessions = {}
    for f in os.listdir(SESSIONS_DIR):
        if f.endswith(".json"):
            sid = f.replace(".json", "")
            try:
                with open(os.path.join(SESSIONS_DIR, f), "r", encoding="utf-8") as file:
                    data = json.load(file)
                    sessions[sid] = data.get("input", "未命名研究")
            except: pass
    return sessions

def coordinator_node(state: AgentState): return coordinator.plan(state)
def scout_node(state: AgentState): return scout.execute(state)
def analyst_node(state: AgentState):
    res = analyst.execute(state)
    res["next_node"] = "wait_plan_discussion"
    return res
def creative_node(state: AgentState):
    res = creative.execute(state)
    res["next_node"] = "wait_brainstorm"
    return res
def coder_node(state: AgentState):
    res = coder.execute(state)
    res["next_node"] = "critic"
    return res
def critic_node(state: AgentState):
    res = critic.execute(state)
    res["next_node"] = "wait_code_review"
    return res
def executor_node(state: AgentState):
    success, logs = run_python_code_safe(state.get("code", ""))
    state["console_output"] = logs
    state["next_node"] = "end" if success else "coder"
    return state

def universal_router(state: AgentState):
    if len(state.get("history", [])) > MAX_STEPS: return "end"
    node = state.get("next_node")
    checkpoints = ["wait_scan_setting", "wait_keyword_confirm", "wait_paper_picking", "wait_plan_discussion", "wait_plan_confirm", "wait_code_review", "wait_brainstorm", "end"]
    if node in checkpoints or node is None: return "end"
    return str(node).strip().lower()

workflow = StateGraph(AgentState)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("scout", scout_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("creative", creative_node)
workflow.add_node("coder", coder_node)
workflow.add_node("critic", critic_node)
workflow.add_node("executor", executor_node)
workflow.set_entry_point("coordinator")

mapping = {"scout": "scout", "analyst": "analyst", "creative": "creative", "coder": "coder", "critic": "critic", "executor": "executor", "end": END}
for name in ["coordinator", "scout", "analyst", "creative", "coder", "critic", "executor"]:
    workflow.add_conditional_edges(name, universal_router, mapping)
app = workflow.compile()
