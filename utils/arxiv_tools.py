import arxiv
from typing import List, Dict

def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    """
    使用 arxiv 库搜索论文
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "summary": result.summary,
            "url": result.pdf_url,
            "authors": [a.name for a in result.authors],
            "published": result.published.strftime("%Y-%m-%d")
        })
    return results
