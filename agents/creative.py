from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import uuid

class CreativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="creative")

    def execute(self, state: AgentState) -> AgentState:
        """
        基于分析报告生成科研灵感
        """
        analysis_results = state.get("analysis", [])
        if not analysis_results:
            state["history"].append("Creative: 未发现分析报告，无法生成灵感。")
            state["next_node"] = "end"
            return state

        print(f"--- [Creative] 正在基于现有研究激发科研灵感... ---")
        
        latest_analysis = analysis_results[-1]
        
        system_prompt = "你是一个充满想象力且逻辑严密的资深科研顾问。请提出 3-5 个具有创新性的科研 Idea。"
        
        try:
            ideas_response = self.call_llm(latest_analysis, system_message=system_prompt)
            state["ideas"].append(ideas_response)
            
            # --- 新增：存入长期记忆 ---
            doc_id = f"idea_{uuid.uuid4().hex[:8]}"
            vector_db.add_record(
                content=ideas_response,
                metadata={"type": "idea", "query": state["input"][:50]},
                doc_id=doc_id
            )
            
            state["history"].append(f"Creative: 已生成灵感报告并存入长期记忆 (ID: {doc_id})。")
        except Exception as e:
            state["history"].append(f"Creative 生成灵感失败: {str(e)}")

        state["next_node"] = "coder" 
        return state
