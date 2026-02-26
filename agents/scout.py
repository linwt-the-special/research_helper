from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.arxiv_tools import search_arxiv
import json

class ScoutAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="scout")

    def execute(self, state: AgentState) -> AgentState:
        """
        生成搜索词并执行 Arxiv 搜索
        """
        user_input = state["input"]
        print(f"--- [Scout] 正在为需求生成搜索关键词... ---")
        
        system_prompt = """你是一个专业的科研情报员。
你的任务是根据用户的需求，生成 1-3 个最适合在 Arxiv 数据库搜索的英文关键词。
请以 JSON 格式输出：
{
  "keywords": "用于搜索的关键词字符串"
}
"""
        response_text = self.call_llm(user_input, system_message=system_prompt)
        
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            search_data = json.loads(cleaned_text)
            keywords = search_data.get("keywords", user_input)
            
            print(f"--- [Scout] 正在 Arxiv 搜索: {keywords} ---")
            papers = search_arxiv(keywords, max_results=3)
            
            state["papers"] = papers
            state["history"].append(f"Scout 找到了 {len(papers)} 篇相关论文。")
            
            # 搜索完后，通常下一步是让分析师进行深度解析
            state["next_node"] = "analyst"
            
        except Exception as e:
            state["history"].append(f"Scout 搜索过程中出现错误: {str(e)}")
            state["next_node"] = "end"
            
        return state
