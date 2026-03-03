from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.arxiv_tools import search_arxiv
from utils.openalex_tools import open_alex_tool
from utils.web_search_tool import web_search_tool

class ScoutAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="scout")

    def execute(self, state: AgentState) -> AgentState:
        # 1. 阶段一：关键词提炼 (无需拦截，自动执行)
        if not state.get("refined_keywords"):
            print("--- [Scout] 正在提炼专业学术搜索词... ---")
            translate_prompt = "将用户的课题方向提炼为 1 个简洁的英文学术搜索短语。直接输出，不要标点。"
            state["refined_keywords"] = self.call_llm(state["input"], system_message=translate_prompt).strip().replace('"', '')
            state["history"].append(f"Scout: 已提炼专业搜索词 '{state['refined_keywords']}'。")

        search_query = state["refined_keywords"]
        year_range = state.get("year_range", "2023-2026")
        from_year = year_range.split("-")[0]
        
        print(f"--- [Scout] 开启混合检索流水线: {search_query} ---")
        
        results = []

        # --- A. 学术搜索: OpenAlex (引用数支撑) ---
        try:
            oa_papers = open_alex_tool.search_papers(search_query, limit=8, from_year=from_year)
            for p in oa_papers:
                results.append({
                    "title": p["title"],
                    "citations": p["citations"],
                    "published": str(p["year"]),
                    "url": p["url"],
                    "summary": "通过学术库 OpenAlex 发现的高影响力论文。",
                    "source": "OpenAlex"
                })
        except: pass

        # --- B. 学术搜索: Arxiv (最新技术支撑) ---
        try:
            arxiv_data = search_arxiv(search_query, max_results=5)
            for ap in arxiv_data:
                results.append({
                    "title": ap["title"],
                    "citations": 0, # Arxiv 通常不带引用数
                    "published": ap["published"],
                    "url": ap["url"],
                    "summary": ap["summary"],
                    "source": "Arxiv"
                })
        except: pass

        # --- C. 通用全网搜索 (实时进展、GitHub、博客) ---
        try:
            web_results = web_search_tool.search(search_query, max_results=5)
            for wr in web_results:
                results.append({
                    "title": wr["title"],
                    "citations": -1, # 标记为非学术引用
                    "published": "最新",
                    "url": wr["url"],
                    "summary": wr["summary"],
                    "source": "Web"
                })
        except: pass

        # 2. 汇总与去重排序
        # 简单去重
        seen_titles = set()
        unique_results = []
        for r in results:
            title_key = r["title"].lower()[:40]
            if title_key not in seen_titles:
                unique_results.append(r)
                seen_titles.add(title_key)

        # 排序：有引用的靠前，其次是 Arxiv，最后是 Web
        unique_results.sort(key=lambda x: x.get("citations", -2), reverse=True)
        
        state["papers"] = unique_results
        
        if unique_results:
            state["history"].append(f"Scout: 混合检索完成，共捕获 {len(unique_results)} 条情报（涵盖学术论文与全网进展）。")
            state["next_node"] = "wait_paper_picking"
        else:
            state["history"].append("Scout: 未能检索到有效信息。")
            state["next_node"] = "end"
            
        return state
