from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import json

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coordinator")

    def plan(self, state: AgentState) -> AgentState:
        current_next = state.get("next_node")
        if current_next in ["scout", "analyst", "coder", "creative", "executor"] and current_next != "coordinator":
            return state

        user_msg = state.get("input", "").lower()
        
        # 快捷解析
        if "复现" in user_msg or "reproduce" in user_msg:
            state["path"], state["next_node"] = "reproduce", "coder"
            return state
        if "讨论" in user_msg or "灵感" in user_msg:
            state["path"], state["next_node"] = "brainstorm", "creative"
            return state
        if "满意" in user_msg or "运行" in user_msg:
            state["next_node"] = "executor"
            return state

        if state.get("papers"):
            return self._parse_user_command(state, state["input"])
        
        return self._initial_planning(state)

    def _initial_planning(self, state: AgentState) -> AgentState:
        print(f"--- [Coordinator] 执行任务规划... ---")
        system_prompt = "分析需求。无论文选'scout'，已有论文选'analyst'。只输出JSON: {'next_node': 'scout'}"
        try:
            resp = self.call_llm(state["input"], system_message=system_prompt)
            data = self.parse_json_robustly(resp)
            state["next_node"] = data.get("next_node", "scout")
        except: state["next_node"] = "scout"
        return state

    def _parse_user_command(self, state: AgentState, command: str) -> AgentState:
        # 确保 LLM 严格输出合法的节点 ID
        system_prompt = """分析用户指令。
必须输出 JSON 格式：{"path": "reproduce/brainstorm", "next_node": "coder/creative/executor"}"""
        context = f"指令: {command}"
        try:
            resp = self.call_llm(context, system_message=system_prompt)
            data = self.parse_json_robustly(resp)
            
            # 严格校验 next_node
            raw_node = data.get("next_node", "end")
            if "coder" in raw_node: state["next_node"] = "coder"
            elif "creative" in raw_node: state["next_node"] = "creative"
            elif "executor" in raw_node: state["next_node"] = "executor"
            else: state["next_node"] = "wait_feedback"
            
            state["path"] = data.get("path", state.get("path", "reproduce"))
        except:
            state["next_node"] = "wait_feedback"
        return state
