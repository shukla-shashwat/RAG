import os
import pickle
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import DATA_DIR, INDEX_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from .embeddings import EmbeddingModel

class Indexer:
    def __init__(self):
        self.index_dir = INDEX_DIR
        os.makedirs(self.index_dir, exist_ok=True)
        self.faiss_path = os.path.join(self.index_dir, "faiss.index")
        self.meta_path = os.path.join(self.index_dir, "metadata.pkl")

    def load_documents(self) -> List[Dict]:
        data_path = Path(DATA_DIR).resolve()
        print(f"[INFO] Scanning for PDFs in: {data_path}")
        pdf_files = list(data_path.glob("**/*.pdf"))
        documents = []
        
        for pdf_file in pdf_files:
            try:
                loader = PyMuPDFLoader(str(pdf_file))
                docs = loader.load()
                print(f"[INFO] Loaded {len(docs)} pages from {pdf_file.name}")
                documents.extend(docs)
            except Exception as e:
                print(f"[ERROR] Failed to load {pdf_file}: {e}")
        return documents

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def build_index(self, force: bool = False):
        if not force and os.path.exists(self.faiss_path) and os.path.exists(self.meta_path):
            print("[INFO] Index already exists. Skipping build. Use --reindex to force rebuild.")
            return

        print("[INFO] Building new index...")
        documents = self.load_documents()
        if not documents:
            print("[WARNING] No documents found to index.")
            return

        chunks = self.chunk_documents(documents)
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [{"text": chunk.page_content, "source": chunk.metadata.get("source", "unknown")} for chunk in chunks]

        print(f"[INFO] Generating embeddings for {len(texts)} chunks...")
        embeddings = EmbeddingModel.embed_documents(texts)
        
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype('float32'))

        print(f"[INFO] Saving index to {self.index_dir}...")
        faiss.write_index(index, self.faiss_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(metadatas, f)
        print("[INFO] Indexing complete.")
