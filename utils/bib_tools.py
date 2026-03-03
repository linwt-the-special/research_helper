import os
from typing import Dict, List

class BibManager:
    def __init__(self, file_path: str = "data/references.bib"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def generate_bib_entry(self, paper: Dict) -> str:
        """
        根据论文元数据生成简单的 BibTeX 条目
        """
        # 生成一个唯一的 ID (例如: AuthorYearTitle的首字母)
        # 这里简化处理，使用标题的第一个词+年份
        title_tag = paper.get("title", "unknown").split()[0].lower()
        year = paper.get("published", "2024")
        entry_id = f"{title_tag}{year}"
        
        bib_template = f"""@article{{{entry_id},
  title = {{{paper.get('title')}}},
  year = {{{year}}},
  url = {{{paper.get('url')}}},
  note = {{Retrieved via ResearchHelper V1.0}},
  abstract = {{{paper.get('summary', '')[:200]}}}
}}
"""
        return bib_template

    def append_to_bib(self, bib_entries: List[str]):
        """将生成的条目追加到本地文件"""
        # 先读取已有的内容防止重复 (简单去重逻辑)
        existing_content = ""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                existing_content = f.read()

        with open(self.file_path, "a", encoding="utf-8") as f:
            for entry in bib_entries:
                # 简单的去重检查
                entry_id = entry.split("{")[1].split(",")[0]
                if entry_id not in existing_content:
                    f.write(entry + "")

bib_manager = BibManager()
