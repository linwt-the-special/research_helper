from agents.base_agent import BaseAgent
from agents.state import AgentState
from pathlib import Path

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coder")

    def execute(self, state: AgentState) -> AgentState:
        """
        根据分析报告生成或修复代码，同时处理审阅意见
        """
        errors = state.get("errors", [])
        feedback = state.get("feedback", "")
        analysis_results = state.get("analysis", [])
        
        output_dir = Path("output/code")
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / "reproduced_algo.py"

        if not errors and not feedback:
            # 初始生成模式
            print(f"--- [Coder] 正在根据分析报告编写算法原型... ---")
            latest_analysis = analysis_results[-1] if analysis_results else "请生成一个 MARL 基础架构。"
            system_prompt = "你是一个顶级的 AI 算法工程师。请根据分析报告编写核心算法 Python 原型，仅输出代码。"
            prompt = latest_analysis
        elif errors:
            # 运行报错修复模式
            print(f"--- [Coder] 检测到运行错误，正在尝试修复... ---")
            system_prompt = "你是一个专业的调试专家。请根据报错信息修复代码，仅输出完整代码。\n报错: {error}".format(error=errors[-1])
            prompt = state.get("code", "")
        else:
            # 审阅意见修复模式
            print(f"--- [Coder] 收到审阅意见，正在优化代码... ---")
            system_prompt = "你是一个专业的算法工程师。请根据以下审阅意见优化代码，仅输出完整代码。\n意见: {fb}".format(fb=feedback)
            prompt = state.get("code", "")

        try:
            code_response = self.call_llm(prompt, system_message=system_prompt)
            code_content = code_response.replace("```python", "").replace("```", "").strip()
            
            state["code"] = code_content
            # 每次修改后重置反馈，进入下一轮审核
            state["feedback"] = "" 
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            
            state["history"].append("Coder 更新了代码。")
            state["next_node"] = "critic" # 修改完后先去审核，不去运行
            
        except Exception as e:
            state["history"].append(f"Coder 操作失败: {str(e)}")
            state["next_node"] = "end"
            
        return state
