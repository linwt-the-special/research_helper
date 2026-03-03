from typing import List, Dict, Any
import json
import re
import ast
from utils.llm_factory import llm_factory

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def call_llm(self, prompt: str, system_message: str = "You are a helpful research assistant.") -> str:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        response = llm_factory.get_completion(self.name, messages)
        return response.choices[0].message.content

    def parse_json_robustly(self, text: str) -> Dict:
        """
        极强鲁棒性的 JSON/Python 字典解析
        """
        # 1. 尝试提取 { ... } 块
        match = re.search(r'\{.*\}', text, re.DOTALL)
        content = match.group() if match else text
        
        # 2. 清理可能的 Markdown 标记
        content = re.sub(r'```[a-z]*', '', content).strip()
        
        # 3. 尝试标准 JSON
        try:
            return json.loads(content)
        except:
            pass
            
        # 4. 尝试 Python literal_eval (处理单引号问题)
        try:
            # 替换一些常见的非法字符
            cleaned_content = content.replace("true", "True").replace("false", "False").replace("null", "None")
            return ast.literal_eval(cleaned_content)
        except:
            raise ValueError(f"无法解析内容为 JSON 或字典: {text[:100]}...")
