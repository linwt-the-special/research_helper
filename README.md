# 科研助手 (Multi-Agent Research Helper) V1.0

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

### 🚀 Quick Start
1.  **Environment**: 
    *   Python 3.10+ is required.
    *   **Docker (Optional but Recommended)**: Used for safe code execution. If not installed, the system will automatically fall back to local execution.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configuration**:
    *   Copy template: `cp configs/config.yaml.example configs/config.yaml`
    *   Edit `configs/config.yaml` with your API Keys.
3.  **Run**:
    ```bash
    streamlit run ui.py
    ```

---

<a name="chinese"></a>

### 🚀 详细安装与运行指南

#### 1. 环境准备
*   **Python**: 建议使用 Python 3.10 或更高版本。
*   **Docker (可选)**: 
    *   **作用**: 用于安全地运行 AI 生成的代码，防止对您的电脑造成潜在影响。
    *   **启用方法**: 只需安装并启动 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 即可。系统会自动检测 Docker 并在必要时后台下载 `python:3.10-slim` 镜像。
    *   **如果不安装**: 系统会**自动切换到本地运行模式**，您依然可以正常使用所有功能。

#### 2. 安装项目依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置 API Key (必须)
1.  在项目根目录下找到 `configs/config.yaml.example`。
2.  将其复制并重命名为 `configs/config.yaml`。
3.  打开该文件，在 `api_key` 处填入您的 Key。

#### 4. 启动程序
我们提供了两种交互方式：
*   **Web 界面 (推荐)**: 拥有可视化图谱和更好的阅读体验。
    ```bash
    streamlit run ui.py
    ```
*   **命令行界面 (CLI)**: 适合极简主义者。
    ```bash
    python main.py
    ```

---

## 🧠 Interaction Logic / 交互逻辑
1.  **Field Scan / 领域扫描**: 输入大方向，系统检索 Arxiv 并生成综述。
2.  **User Intervention / 人工干预**: 系统暂停，供你查看图谱、指定小方向并选择路径。
3.  **Iteration / 迭代产出**: 支持代码复现或灵感碰撞。
4.  **Export / 成果导出**: 侧边栏一键导出完整研究报告。

## 📜 License / 许可证
Free for personal use. Commercial use requires authorization. / 个人使用免费，商业用途需授权。
