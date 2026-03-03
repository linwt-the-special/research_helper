from agents.base_agent import BaseAgent
from agents.state import AgentState

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="summarizer")

    def execute(self, history: list) -> str:
        print(f"--- [Summarizer] 正在压缩历史上下文... ---")
        system_prompt = """你是一个高效的科研档案管理员。
请对以下多智能体协作的历史记录进行精简总结。
要求：
1. 保留核心结论、找到的关键论文标题、以及已确认的研究思路。
2. 剔除重复思考和冗余对话。
3. 字数控制在 500 字以内。"""
        history_text = "\n".join(history)
        summary = self.call_llm(history_text, system_message=system_prompt)
        return summary

summarizer = SummarizerAgent()
