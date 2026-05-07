from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from .config import EMBEDDING_MODEL_NAME

class EmbeddingModel:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL_NAME}")
            # Explicitly using CPU can be safer/faster for small models if GPU init is slow, 
            # but usually auto is fine. We'll stick to default but cache the instance.
            cls._instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return cls._instance

    @staticmethod
    def embed_documents(texts: List[str]) -> np.ndarray:
        model = EmbeddingModel.get_instance()
        return model.encode(texts, show_progress_bar=True)

    @staticmethod
    def embed_query(text: str) -> np.ndarray:
        model = EmbeddingModel.get_instance()
        return model.encode([text])[0]
