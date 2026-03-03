from agents.base_agent import BaseAgent
from agents.state import AgentState

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="critic")

    def execute(self, state: AgentState) -> AgentState:
        analysis = state.get("analysis", [])
        code = state.get("code", "")
        
        if not analysis or not code:
            state["history"].append("Critic: 缺少分析或代码。")
            state["next_node"] = "end"
            return state

        system_prompt = """你是一个严谨的期刊审稿人。检查代码是否实现了报告中的方法论。
        合格请回复 [PASSED]，不合格请回复 [REJECTED] 并列出建议。"""
        user_content = f"【报告】:\n{analysis[-1]}\n\n【代码】:\n{code}"
        
        try:
            feedback = self.call_llm(user_content, system_message=system_prompt)
            state["feedback"] = feedback
            if "[PASSED]" in feedback:
                state["history"].append("Critic: 审核通过。")
                state["next_node"] = "executor"
            else:
                state["history"].append("Critic: 审核未通过，要求修改。")
                state["next_node"] = "coder"
        except Exception as e:
            state["history"].append(f"Critic 异常: {str(e)}")
            state["next_node"] = "end"
        return state
