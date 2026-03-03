import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any

class VectorDB:
    def __init__(self, db_path: str = "data/chroma_db"):
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="research_notes",
            embedding_function=self.ef
        )

    def add_record(self, content: str, metadata: Dict[str, Any], doc_id: str):
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, query_text: str, n_results: int = 3):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

vector_db = VectorDB()
