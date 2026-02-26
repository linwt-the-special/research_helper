from typing import Annotated, TypedDict, List, Dict
import operator

class AgentState(TypedDict):
    # 用户原始输入
    input: str
    # 当前研究上下文
    research_context: str
    # 论文列表
    papers: List[Dict]
    # 提取的分析结果
    analysis: List[str]
    # 创意/想法
    ideas: List[str]
    # 代码片段
    code: str
    # 错误日志
    errors: List[str]
    # 审核意见
    feedback: str
    # 任务历史记录 (用于追踪流程)
    history: Annotated[List[str], operator.add]
    # 下一个要执行的节点
    next_node: str
