from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.coordinator import CoordinatorAgent
from utils.config_loader import config_loader

from agents.scout import ScoutAgent
from agents.analyst import AnalystAgent
from agents.coder import CoderAgent
from agents.critic import CriticAgent
from agents.creative import CreativeAgent
from utils.executor import run_python_code

# 初始化智能体
coordinator = CoordinatorAgent()
scout = ScoutAgent()
analyst = AnalystAgent()
coder = CoderAgent()
critic = CriticAgent()
creative = CreativeAgent()

# 计数器
GLOBAL_STEP_COUNT = 0
MAX_STEPS = 20 # 调高一点，因为增加了创意节点

def coordinator_node(state: AgentState):
    """协调员节点：负责任务规划"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Coordinator] ---")
    return coordinator.plan(state)

def scout_node(state: AgentState):
    """侦察员节点：负责文献搜索"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Scout] ---")
    return scout.execute(state)

def analyst_node(state: AgentState):
    """分析师节点：负责深度解析"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Analyst] ---")
    return analyst.execute(state)

def coder_node(state: AgentState):
    """程序员节点：负责代码生成/修复"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Coder] ---")
    return coder.execute(state)

def critic_node(state: AgentState):
    """评论家节点：负责学术审阅"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Critic] ---")
    return critic.execute(state)

def creative_node(state: AgentState):
    """创意家节点：负责灵感启发"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Creative] ---")
    return creative.execute(state)

def executor_node(state: AgentState):
    """执行器节点：运行代码并捕获错误"""
    print(f"--- [Step {GLOBAL_STEP_COUNT}] [Node: Executor] ---")
    file_path = "output/code/reproduced_algo.py"
    success, logs = run_python_code(file_path)
    
    if success:
        print("--- [Executor] 代码运行成功！ ---")
        state["history"].append("Executor: 代码运行成功。")
        state["errors"] = []
        state["next_node"] = "creative" # 代码跑通后，让创意家基于实现结果再想点新的
    else:
        print(f"--- [Executor] 代码运行失败... ---")
        state["history"].append("Executor: 代码报错。")
        state["errors"].append(logs)
        
        if len(state["errors"]) > 3:
            state["next_node"] = "creative" # 实在修不好也去创意家看看
        else:
            state["next_node"] = "coder"
            
    return state

def router(state: AgentState):
    """通用路由逻辑"""
    global GLOBAL_STEP_COUNT
    GLOBAL_STEP_COUNT += 1
    
    if GLOBAL_STEP_COUNT > MAX_STEPS:
        print("--- [Router] 达到全局步数上限，强制终止任务。 ---")
        return END
        
    next_node = state.get("next_node")
    if next_node == "end":
        return END
    return next_node

# 构建状态图
workflow = StateGraph(AgentState)

workflow.add_node("coordinator", coordinator_node)
workflow.add_node("scout", scout_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("coder", coder_node)
workflow.add_node("critic", critic_node)
workflow.add_node("creative", creative_node)
workflow.add_node("executor", executor_node)

workflow.set_entry_point("coordinator")

# 配置所有需要路由的节点
workflow.add_conditional_edges("coordinator", router)
workflow.add_conditional_edges("scout", router)
workflow.add_conditional_edges("analyst", router)
workflow.add_conditional_edges("coder", router)
workflow.add_conditional_edges("critic", router)
workflow.add_conditional_edges("creative", router)
workflow.add_conditional_edges("executor", router)

# 编译图
app = workflow.compile()

def run_research_assistant(query: str):
    """运行科研助手"""
    initial_state = {
        "input": query,
        "research_context": "",
        "papers": [],
        "analysis": [],
        "ideas": [],
        "code": "",
        "errors": [],
        "feedback": "",
        "history": [],
        "next_node": ""
    }
    
    print(f"用户查询: {query}\n")
    for output in app.stream(initial_state):
        for node_name, state_update in output.items():
            if "history" in state_update and state_update["history"]:
                print(f"日志: {state_update['history'][-1]}")
            
            # 如果有新点子，打印出来
            if "ideas" in state_update and state_update["ideas"]:
                print("\n✨ 创意家生成的科研灵感报告 ✨")
                print(state_update["ideas"][-1])
                print("--------------------------------\n")
    
    print("\n--- 任务执行完毕 ---")

if __name__ == "__main__":
    user_query = "找一篇 MARL 论文，分析核心算法并尝试为我生成一个 Python 实现原型，最后基于这些研究给我 3 个创新的研究 Idea。"
    run_research_assistant(user_query)
