from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import uuid

class CreativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="creative")

    def execute(self, state: AgentState) -> AgentState:
        analysis_results = state.get("analysis", [])
        if not analysis_results:
            state["history"].append("Creative: 缺少分析报告。")
            state["next_node"] = "end"
            return state

        system_prompt = "你是一个富有想象力的科研顾问。基于分析报告提出 3-5 个创新科研 Idea。用 Markdown 输出。"
        try:
            ideas_response = self.call_llm(analysis_results[-1], system_message=system_prompt)
            state["ideas"].append(ideas_response)
            
            doc_id = f"idea_{uuid.uuid4().hex[:8]}"
            vector_db.add_record(
                content=ideas_response,
                metadata={"type": "idea", "query": state["input"][:50]},
                doc_id=doc_id
            )
            state["history"].append(f"Creative: 已生成灵感。")
            # 明确设置下一跳为交互等待点
            state["next_node"] = "wait_brainstorm"
        except Exception as e:
            state["history"].append(f"Creative 失败: {str(e)}")
            state["next_node"] = "end"

        return state
