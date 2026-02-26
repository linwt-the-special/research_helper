# 科研助手 (Multi-Agent Research Helper)

基于多智能体架构的科研全流程助手，支持文献搜索、横向对比、灵感启发、代码复现及自动纠错。

## 🌟 核心特性

*   **多智能体协同**: 协调员、侦察员、分析师、创意家、程序员、评论家六大角色各司其职。
*   **全自动工作流**: 从一个简单的科研想法出发，自动完成搜索到代码生成的全链路。
*   **自修复代码循环**: 内置执行器与评论家，生成代码后自动运行并根据报错或审阅意见进行迭代。
*   **长期记忆 (RAG)**: 使用 ChromaDB 存储历史分析结果，支持跨任务知识调用。
*   **模型无关**: 支持 Kimi, GPT-4o, DeepSeek, Gemini 等多种 API，支持本地模型。

## 🚀 快速开始

### 1. 安装依赖
确保你已安装 Python 3.10+：
```bash
pip install -r requirements.txt
```

### 2. 配置模型 (必须)

1. 复制项目中的模板文件：
   ```bash
   cp configs/config.yaml.example configs/config.yaml
   ```
2. 编辑 `configs/config.yaml`，填入你的 API Key 和模型地址。

本项目基于 **LiteLLM**，支持绝大多数大模型配置示例：
*   **Kimi (Moonshot)**: `api_base: "https://api.moonshot.cn/v1"`
*   **ChatAnywhere**: `api_base: "https://api.chatanywhere.tech/v1"`


### 3. 运行助手
直接运行 `main.py` 并在其中修改你的查询需求：
```bash
python main.py
```

## 📁 项目结构

*   `agents/`: 智能体核心逻辑定义
*   `utils/`: PDF 处理、Arxiv 搜索、向量数据库、代码执行等工具类
*   `configs/`: 配置文件目录
*   `output/`: 自动生成的复现代码存放在 `output/code/`
*   `data/`: 存储下载的 PDF 和 ChromaDB 数据库

## 🛠️ 测试组件
你可以通过运行以下脚本验证各模块功能：
*   `python tests/test_components.py`: 验证搜索、下载、解析全链路。
*   `python tests/test_memory.py`: 验证 RAG 向量检索。

## 📜 许可证
个人使用免费，商业用途需授权。详见 `LICENSE` 文件。
