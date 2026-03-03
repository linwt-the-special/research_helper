from duckduckgo_search import DDGS
from typing import List, Dict

class WebSearchTool:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        无需 API Key 的通用搜索，获取网页标题、链接和摘要
        """
        print(f"--- [WebSearch] 正在全网检索: {query} ---")
        results = []
        try:
            # 使用 text 搜索获取网页内容
            response = self.ddgs.text(query, max_results=max_results)
            for r in response:
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "summary": r.get("body"),
                    "source": "Web"
                })
        except Exception as e:
            print(f"Web Search 异常: {e}")
        return results

web_search_tool = WebSearchTool()
