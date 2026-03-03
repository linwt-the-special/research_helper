from agents.base_agent import BaseAgent
from agents.state import AgentState
from utils.vector_db import vector_db
import uuid

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="analyst")

    def execute(self, state: AgentState) -> AgentState:
        all_papers = state.get("papers", [])
        selected_ids = state.get("selected_paper_ids", [])
        target_papers = [all_papers[i] for i in selected_ids if i < len(all_papers)] if selected_ids else all_papers[:2]

        if not target_papers:
            state["history"].append("Analyst: 论文列表为空，强制回退 Scout。")
            state["next_node"] = "scout"
            return state

        print(f"--- [Analyst] 正在分析文献并提取参考指标... ---")
        context = "【待分析文献】:\n"
        for p in target_papers:
            context += f"标题: {p['title']}\n摘要: {p['summary']}\n---\n"

        system_prompt = """你是一个严谨的学术分析师。请根据文献完成：
1. 提取各论文的实验结果（如精度、耗时等指标），生成一个 Markdown 表格作为 SOTA 参考表。
2. 撰写一份“文献调研参考报告”，分析各论文的技术路线和局限性。
请务必将 SOTA 表格放在 <SOTA_TABLE> 标签内，报告放在 <REPORT> 标签内。"""
        
        try:
            resp = self.call_llm(context, system_message=system_prompt)
            
            # 解析 SOTA 表
            if "<SOTA_TABLE>" in resp:
                state["sota_table"] = resp.split("<SOTA_TABLE>")[1].split("</SOTA_TABLE>")[0].strip()
            
            # 解析 参考报告
            if "<REPORT>" in resp:
                state["analysis_report"] = resp.split("<REPORT>")[1].split("</REPORT>")[0].strip()
            else:
                state["analysis_report"] = resp.split("<SOTA_TABLE>")[0].strip()

            state["history"].append("Analyst: 文献深度分析完成。参考信息已展示在右侧看板。")
            # 关键：下一步进入“计划讨论”阶段
            state["next_node"] = "wait_plan_discussion"
        except Exception as e:
            state["history"].append(f"Analyst 失败: {str(e)}")
            state["next_node"] = "end"

        return state
