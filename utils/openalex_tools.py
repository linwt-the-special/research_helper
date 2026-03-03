import requests
from typing import List, Dict
import time

class OpenAlexTool:
    def __init__(self):
        self.base_url = "https://api.openalex.org/works"

    def search_papers(self, query: str, limit: int = 10, from_year: str = "2023") -> List[Dict]:
        """
        通过 OpenAlex API 搜索论文（无需 API Key）
        """
        print(f"--- [OpenAlex] 正在独立检索: {query} ---")
        
        # 构造参数：搜索关键词，过滤年份，按引用数降序
        params = {
            "search": query,
            "filter": f"from_publication_date:{from_year}-01-01",
            "sort": "cited_by_count:desc",
            "per_page": limit,
            "select": "title,id,cited_by_count,publication_year,abstract_inverted_index,doi"
        }
        
        try:
            # 加上 User-Agent 是个好习惯，加入邮箱可以进入 Polite Pool
            headers = {"User-Agent": "ResearchHelper/1.0 (mailto:your-email@example.com)"}
            response = requests.get(self.base_url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for work in data.get("results", []):
                    # OpenAlex 的摘要是倒排索引格式，需要简单转换或直接跳过（我们有 Arxiv 补充）
                    results.append({
                        "title": work.get("title"),
                        "citations": work.get("cited_by_count", 0),
                        "year": work.get("publication_year"),
                        "url": work.get("doi") or f"https://openalex.org/{work.get('id')}",
                        "source": "OpenAlex"
                    })
                return results
            else:
                print(f"--- [OpenAlex] API 返回错误: {response.status_code} ---")
                return []
        except Exception as e:
            print(f"--- [OpenAlex] 检索异常: {str(e)} ---")
            return []

open_alex_tool = OpenAlexTool()
