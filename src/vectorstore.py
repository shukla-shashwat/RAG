import os
import faiss
import numpy as np
import pickle
from typing import List, Any
from sentence_transformers import SentenceTransformer
from src.embeddings import EmbeddingPipeline

class FaissVectorStore:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2" , chunk_size: int = 1000, chunk_overlap: int = 200   ):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata = []
        self.embedding_model = embedding_model  
        self.model = SentenceTransformer(embedding_model)   
        self.chunk_size = chunk_size 
        self.chunk_overlap = chunk_overlap 
        print(f"[INFO] Loaded embedding model: {embedding_model}")

    def build_from_documents(self, documents: List[Any]):
        """Build FAISS index from documents.

        Args:
            documents (List[Any]): List of documents to be indexed.
        """
        print(f"[INFO] Building FAISS index from {len(documents)} documents...")

        emb_pipe = EmbeddingPipeline(model_name=self.embedding_model, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = emb_pipe.chunk_documents(documents)
        embeddings = emb_pipe.embed_documents(chunks)
        metadata  =[{"text": chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype('float32'), metadata)
        self.save()
        print(f"[INFO] FAISS index built and saved to {self.persist_dir}.")

    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Any] = None):
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadata:
            self.metadata.extend(metadata)
        print(f"[INFO] Added {embeddings.shape[0]} embeddings to the index.")

    def save(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] FAISS index and metadata saved to (self.persist_dir)")

    def load(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        if os.path.exists(faiss_path) and os.path.exists(meta_path):
            self.index = faiss.read_index(faiss_path)
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"[INFO] FAISS index and metadata loaded from {self.persist_dir}.")
        else:
            print(f"[WARNING] FAISS index or metadata not found in {self.persist_dir}.")

    def search(self,query_embedding: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
           meta = self.metadata[idx] if idx < len(self.metadata) else None
           results.append({"index": idx, "metadata": meta, "distance": dist})
        return results
    
    def query(self, query_text: str, top_k: int = 5):
        print(f"[INFO] Queryin vector store for: {query_text}")
        query_embedding = self.model.encode([query_text]).astype('float32')
        return self.search(query_embedding, top_k=top_k)
