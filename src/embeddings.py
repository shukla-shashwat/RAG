from typing import List, Any, Union, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer   
import numpy as np
from src.data_loader import load_all_documents

class EmbeddingPipeline:
    def __init__(self,model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self. model = SentenceTransformer(model_name)
        print(f"[INFO] Loaded embedding model: {model_name}")

    def chunk_documents(self,document: List[Any]) -> List[Any]:
        """Chunk documents into smaller pieces for embedding.

        Args:
            document (List[Any]): List of documents to be chunked.

        Returns:
            List[dict]: List of chunked documents with metadata.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            # length_function=len,
            separators = ["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(document)
        print(f"[INFO] SPlit {len(document)} documents into {len(chunks)} chunks.")
        return chunks 

    def embed_documents(self,chunks: List[Any]) -> np.ndarray:
        text = [chunk.page_content for chunk in chunks]
        print(f"[INFO]Generating embeddings for {len(text)} chunks.")
        embeddings = self.model.encode(text, show_progress_bar=True)
        print(f"[INFO]Generated embeddings with shape: {embeddings.shape}")
        return embeddings