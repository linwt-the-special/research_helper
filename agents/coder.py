from agents.base_agent import BaseAgent
from agents.state import AgentState
from pathlib import Path

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coder")

    def execute(self, state: AgentState) -> AgentState:
        errors, feedback = state.get("errors", []), state.get("feedback", "")
        path, sub_dir = state.get("path", "reproduce"), state.get("sub_direction", "")
        output_dir = Path("output/code")
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / "reproduced_algo.py"

        if not errors and not feedback:
            if path == "brainstorm":
                latest = state.get("ideas", [])[-1] if state.get("ideas") else ""
                sys_msg = f"你是一个顶级算法工程师。实现思路: {sub_dir}。根据灵感报告写 Python 代码，仅输出代码。"
                prompt = latest
            else:
                latest = state.get("analysis", [])[-1] if state.get("analysis") else ""
                sys_msg = f"你是一个顶级算法工程师。复现目标: {sub_dir}。根据分析报告写 Python 代码，仅输出代码。"
                prompt = latest
        elif errors:
            sys_msg = f"你是一个调试专家。修复报错: {errors[-1]}。仅输出完整代码。"
            prompt = state.get("code", "")
        else:
            sys_msg = f"你是一个算法工程师。根据意见优化代码: {feedback}。仅输出完整代码。"
            prompt = state.get("code", "")

        try:
            resp = self.call_llm(prompt, system_message=sys_msg)
            code = resp.replace("```python", "").replace("```", "").strip()
            state["code"], state["feedback"] = code, ""
            with open(file_path, "w", encoding="utf-8") as f: f.write(code)
            state["history"].append(f"Coder: 已生成/更新代码 ({path})。")
            state["next_node"] = "critic"
        except Exception as e:
            state["history"].append(f"Coder 失败: {str(e)}")
            state["next_node"] = "end"
        return state
