import os
import pickle
import faiss
import numpy as np
from typing import List, Dict, Tuple

from .config import INDEX_DIR
from .embeddings import EmbeddingModel

class Retriever:
    def __init__(self):
        self.index_dir = INDEX_DIR
        self.faiss_path = os.path.join(self.index_dir, "faiss.index")
        self.meta_path = os.path.join(self.index_dir, "metadata.pkl")
        self.index = None
        self.metadata = []
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.faiss_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.faiss_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"[INFO] Loaded index with {self.index.ntotal} vectors.")
        else:
            print("[WARNING] Index not found. Please run indexing first.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.index is None:
            return []
        
        query_vector = EmbeddingModel.embed_query(query)
        # Faiss expects 2D array
        D, I = self.index.search(np.array([query_vector]).astype('float32'), top_k)
        
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx < len(self.metadata) and idx >= 0:
                item = self.metadata[idx].copy()
                item['distance'] = float(dist)
                results.append(item)
        return results
