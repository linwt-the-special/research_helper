from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import json
import uuid

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="analyst")

    def execute(self, state: AgentState) -> AgentState:
        """
        对搜索到的多篇论文进行横向对比分析
        """
        papers = state.get("papers", [])
        if not papers:
            state["history"].append("Analyst 未发现待处理论文列表。")
            state["next_node"] = "end"
            return state

        print(f"--- [Analyst] 正在对比分析 {len(papers)} 篇论文... ---")
        
        # 聚合多篇论文的信息
        aggregated_context = ""
        for i, paper in enumerate(papers[:3]):
            aggregated_context += f"论文 {i+1}:\n标题: {paper['title']}\n摘要: {paper['summary']}\n---\n"

        system_prompt = "你是一个专业的科研评论员。请进行横向对比分析，输出 Markdown 报告。"
        
        try:
            analysis_result = self.call_llm(aggregated_context, system_message=system_prompt)
            state["analysis"].append(analysis_result)
            
            # --- 新增：存入长期记忆 ---
            doc_id = f"analyst_{uuid.uuid4().hex[:8]}"
            vector_db.add_record(
                content=analysis_result,
                metadata={"type": "analysis", "papers_count": len(papers), "query": state["input"][:50]},
                doc_id=doc_id
            )
            
            state["history"].append(f"Analyst 完成分析并已存入长期记忆 (ID: {doc_id})。")
        except Exception as e:
            state["history"].append(f"Analyst 分析失败: {str(e)}")

        state["next_node"] = "creative"
        return state
