import chromadb
from chromadb.utils import embedding_functions
import os
from utils.config_loader import config_loader
from typing import List, Dict, Any

class VectorDB:
    def __init__(self, db_path: str = "data/chroma_db"):
        os.makedirs(db_path, exist_ok=True)
        # 初始化持久化客户端
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 使用默认的 embedding 函数 (或者可以配置为 OpenAI/Gemini)
        # 为了简单且免费，我们先用 chromadb 自带的默认模型
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="research_notes",
            embedding_function=self.ef
        )

    def add_record(self, content: str, metadata: Dict[str, Any], doc_id: str):
        """
        向数据库添加一条记录（如分析报告或创意）
        """
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3):
        """
        语义搜索最相关的历史记录
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

# 单例模式
vector_db = VectorDB()
