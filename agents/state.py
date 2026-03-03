from typing import Annotated, TypedDict, List, Dict
import operator

class AgentState(TypedDict):
    # --- 核心对话 (展示在左侧) ---
    chat_history: List[Dict[str, str]] # [{'role': 'user/assistant', 'content': '...'}]
    
    # --- 交互决策参数 ---
    input: str              # 最近一次用户输入
    year_range: str         
    refined_keywords: str   
    selected_paper_ids: List[int] 
    
    # --- 研究数据 (展示在右侧) ---
    papers: List[Dict]      
    analysis_report: str    
    sota_table: str         
    research_plan: str      
    ideas: List[str]
    
    # --- 开发与执行 ---
    code: str
    errors: List[str]
    console_output: str     
    feedback: str           
    
    # --- 内部流程控制 (展示在后台日志) ---
    history: Annotated[List[str], operator.add]
    next_node: str
    session_id: str
