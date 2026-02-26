import os
import requests
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional

def download_pdf(url: str, save_dir: str = "data/pdfs") -> Optional[str]:
    """
    下载 PDF 文件并返回本地路径
    """
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    file_name = url.split("/")[-1]
    if not file_name.endswith(".pdf"):
        file_name += ".pdf"
    
    file_path = os.path.join(save_dir, file_name)
    
    if os.path.exists(file_path):
        return file_path

    print(f"正在下载 PDF: {url}...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        print(f"下载 PDF 失败: {str(e)}")
    return None

def extract_text_from_pdf(file_path: str, max_pages: int = 10) -> str:
    """
    从 PDF 中提取纯文本 (默认限制页数以节省上下文)
    """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            # 只取前 max_pages 页，通常对于摘要和核心方法论足够了
            for page in doc[:max_pages]:
                text += page.get_text()
    except Exception as e:
        text = f"提取文本失败: {str(e)}"
    return text
