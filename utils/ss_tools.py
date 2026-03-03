import requests
from typing import List, Dict, Optional
import time
from utils.config_loader import config_loader

class SemanticScholarTool:
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"

    def _get_api_key(self):
        try:
            # 尝试从 scout 的配置中获取 api_key
            conf = config_loader.get_agent_config("scout")
            return conf.get("ss_api_key")
        except: return None

    def search_papers(self, query: str, limit: int = 10, year_range: str = None) -> List[Dict]:
        url = f"{self.base_url}/paper/search"
        api_key = self._get_api_key()
        headers = {"x-api-key": api_key} if api_key else {}
        
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,citationCount,influentialCitationCount,externalIds,url,abstract"
        }
        if year_range: params["year"] = year_range

        # 增加指数退避重试
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=20)
                if response.status_code == 200:
                    return response.json().get("data", [])
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 10
                    print(f"--- [SS Tool] 触发频率限制，等待 {wait_time} 秒后重试... ---")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"--- [SS Tool] API 错误: {response.status_code} ---")
                    return []
            except Exception as e:
                print(f"--- [SS Tool] 网络异常: {str(e)} ---")
                return []
        return []

ss_tool = SemanticScholarTool()
