from agents.base_agent import BaseAgent
from agents.state import AgentState

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="critic")

    def execute(self, state: AgentState) -> AgentState:
        """
        对分析报告和生成的代码进行交叉审核
        """
        analysis = state.get("analysis", [])
        code = state.get("code", "")
        
        if not analysis or not code:
            state["history"].append("Critic: 缺少分析报告或代码，无法审核。")
            state["next_node"] = "end"
            return state

        print(f"--- [Critic] 正在进行学术审核与代码审计... ---")
        
        latest_analysis = analysis[-1]
        
        system_prompt = """你是一个严谨的顶级期刊审稿人（如 Nature/Science/NIPS 审稿人）。
我会给你一份论文分析报告，以及一份初步的 Python 实现原型。
你的任务是：
1. 检查代码是否真的实现了分析报告中提到的核心方法论。
2. 寻找逻辑漏洞或过度简化的地方。
3. 给出具体的改进建议。

如果代码质量合格，请在回复开头明确写出 [PASSED]。
如果不合格，请在回复开头明确写出 [REJECTED]，并详细列出需要修改的点。
"""
        user_content = f"【分析报告】:\n{latest_analysis}\n\n【实现代码】:\n{code}"
        
        try:
            feedback = self.call_llm(user_content, system_message=system_prompt)
            state["feedback"] = feedback
            
            if "[PASSED]" in feedback:
                state["history"].append("Critic: 审核通过 [PASSED]。")
                state["next_node"] = "executor" # 通过了才去跑实验
            else:
                state["history"].append("Critic: 审核未通过 [REJECTED]，要求修改。")
                state["next_node"] = "coder" # 退回程序员重写
                
        except Exception as e:
            state["history"].append(f"Critic 审核过程异常: {str(e)}")
            state["next_node"] = "end"
            
        return state
