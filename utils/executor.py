import docker
import os
import subprocess
import sys
from pathlib import Path

class CodeExecutor:
    def __init__(self, image="python:3.10-slim"):
        self.image = image
        self.use_docker = False
        self.client = None
        
        try:
            self.client = docker.from_env()
            self.client.ping() 
            self.use_docker = True
            print("--- [Executor] Docker 环境连接成功。 ---")
        except Exception as e:
            print(f"--- [Executor] Docker 未就绪: {str(e)}。将回退至本地模式。 ---")
            self.use_docker = False

    def _prepare_image(self):
        """尝试获取或拉取镜像，如果失败则临时降级"""
        if not self.use_docker: return False
        
        try:
            self.client.images.get(self.image)
            return True
        except docker.errors.ImageNotFound:
            print(f"--- [Executor] 正在下载 Docker 镜像 {self.image}，这可能需要几分钟... ---")
            try:
                self.client.images.pull(self.image)
                print(f"--- [Executor] 镜像下载完成。 ---")
                return True
            except Exception as e:
                print(f"--- [Executor] 镜像下载失败: {str(e)}。本次运行将临时切换到本地模式。 ---")
                return False

    def run_code(self, code_content: str, timeout: int = 60):
        temp_dir = Path("data/sandbox")
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / "sandbox_app.py"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)

        # 每次运行前检查镜像是否准备好
        if self.use_docker and self._prepare_image():
            return self._run_docker(file_path, timeout)
        else:
            return self._run_local(file_path, timeout)

    def _run_docker(self, file_path, timeout):
        print(f"--- [Executor] 正在 Docker 容器中运行... ---")
        try:
            container = self.client.containers.run(
                image=self.image,
                command=f"python /app.py",
                volumes={os.path.abspath(file_path): {'bind': '/app.py', 'mode': 'ro'}},
                detach=False,
                remove=True,
                mem_limit="256m",
                timeout=timeout
            )
            return True, container.decode("utf-8")
        except Exception as e:
            return False, f"Docker 运行异常: {str(e)}"

    def _run_local(self, file_path, timeout):
        print(f"--- [Executor] 正在本地环境运行... ---")
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True, text=True, timeout=timeout, encoding="utf-8"
            )
            return (True, result.stdout) if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)

executor = CodeExecutor()

def run_python_code_safe(code_content: str):
    return executor.run_code(code_content)
