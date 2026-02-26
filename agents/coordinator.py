from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import json

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coordinator")

    def plan(self, state: AgentState) -> AgentState:
        """
        根据用户输入制定研究计划，并检索长期记忆
        """
        # --- 新增：检索长期记忆 ---
        print(f"--- [Coordinator] 正在检索长期记忆... ---")
        memories = vector_db.query(state["input"], n_results=1)
        past_findings = ""
        if memories and memories["documents"] and memories["documents"][0]:
            past_findings = "\n【历史研究参考】:\n" + memories["documents"][0][0][:1000]
            print(f"--- [Coordinator] 发现相关历史记录，已加入上下文。 ---")

        system_prompt = """你是一个高水平科研团队的协调员。
你的任务是分析用户的科研需求，并决定下一步应该执行什么任务。

关键原则：
1. 如果 state 中没有任何论文数据 (papers 列表为空)，你必须首先执行 'scout'。
2. 你可以参考提供的【历史研究参考】来优化你的决策。

可选任务: 'scout', 'analyst', 'coder', 'creative'。

请以 JSON 格式输出：
{{
  "reasoning": "你的分析逻辑",
  "next_node": "scout/analyst/coder/creative",
  "context_summary": "对用户需求的简要总结"
}}
"""
        user_input = f"当前状态: 论文数={len(state.get('papers', []))}\n用户需求: {state['input']}\n{past_findings}"
        
        response_text = self.call_llm(user_input, system_message=system_prompt)
        
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            plan_data = json.loads(cleaned_text)
            
            state["next_node"] = plan_data.get("next_node", "scout")
            state["research_context"] = plan_data.get("context_summary", "")
            state["history"].append(f"Coordinator 计划: {plan_data.get('reasoning')}")
            
        except Exception as e:
            state["next_node"] = "scout"
            state["history"].append("Coordinator 计划解析失败，默认转入 Scout。")
            
        return state

