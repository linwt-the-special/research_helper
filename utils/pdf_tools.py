import os
import requests
import fitz
from pathlib import Path
from typing import Optional

def download_pdf(url: str, save_dir: str = "data/pdfs") -> Optional[str]:
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    file_name = url.split("/")[-1]
    if not file_name.endswith(".pdf"): file_name += ".pdf"
    file_path = os.path.join(save_dir, file_name)
    if os.path.exists(file_path): return file_path

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(file_path, "wb") as f: f.write(response.content)
            return file_path
    except: pass
    return None

def extract_text_from_pdf(file_path: str, max_pages: int = 10) -> str:
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc[:max_pages]: text += page.get_text()
    except Exception as e:
        text = f"提取失败: {str(e)}"
    return text
