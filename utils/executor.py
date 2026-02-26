import subprocess
import sys
import os

def run_python_code(file_path: str, timeout: int = 30):
    """
    运行指定的 Python 文件并捕获输出和错误
    """
    print(f"--- [Executor] 正在尝试运行: {file_path} ---")
    try:
        # 使用当前环境的 Python 解释器运行
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8"
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "代码运行超时。"
    except Exception as e:
        return False, str(e)
