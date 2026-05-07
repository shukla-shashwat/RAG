"""Minimal RAG inference script.

Usage:
  python rag_run.py --query "What is RAG?"

This script loads a FAISS index and metadata, embeds a query with
SentenceTransformers, retrieves top-k documents, and uses
ChatGoogleGenerativeAI to generate an answer from the retrieved context.
"""
import argparse
import faiss
import pickle
from typing import Tuple, List

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

FAISS_PATH = "faiss_store/faiss.index"
META_PATH = "faiss_store/metadata.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"


def load_vector_store(faiss_path: str = FAISS_PATH, meta_path: str = META_PATH) -> Tuple[faiss.Index, List[dict]]:
    """Load FAISS index and metadata pickle file.

    Returns (index, metadata_list) where metadata_list is a list-like mapping id->dict.
    """
    index = faiss.read_index(faiss_path)
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def embed_query(model: SentenceTransformer, text: str) -> np.ndarray:
    emb = model.encode([text])
    emb = np.asarray(emb, dtype="float32")
    return emb


def faiss_search(index: faiss.Index, embedding: np.ndarray, top_k: int = 5):
    distances, ids = index.search(embedding, top_k)
    return ids[0], distances[0]


def generate_answer(query: str, context: str):
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("ChatGoogleGenerativeAI is not available. Install langchain_google_genai or adjust the LLM call.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        max_tokens=700,
    )

    prompt = f"""Use this context to answer the question.


Context:
{context}

Question: {query}

Answer:
"""

    # The library may return different shapes; try to handle common cases
    response = llm.invoke(prompt)
    # prefer .content if present, else stringify
    return getattr(response, "content", str(response))


def rag(query: str, top_k: int = 3, faiss_path: str = FAISS_PATH, meta_path: str = META_PATH) -> str:
    index, metadata = load_vector_store(faiss_path, meta_path)
    model = SentenceTransformer(EMBED_MODEL)

    embedding = embed_query(model, query)
    ids, distances = faiss_search(index, embedding, top_k=top_k)

    # ids may contain -1 for missing; filter and guard
    texts = []
    for i in ids:
        if i is None or int(i) < 0:
            continue
        try:
            texts.append(metadata[int(i)].get("text", ""))
        except Exception:
            # fallback in case metadata is a dict keyed by str ids
            texts.append(metadata.get(int(i), {}).get("text", "") if isinstance(metadata, dict) else "")

    context = "\n\n".join([t for t in texts if t])
    if not context:
        context = ""  # empty context

    answer = generate_answer(query, context)
    return answer


def main():
    parser = argparse.ArgumentParser(description="Minimal RAG runner")
    parser.add_argument("--query", "-q", type=str, help="Question to ask", required=False)
    parser.add_argument("--top-k", "-k", type=int, default=3, help="Number of docs to retrieve")
    parser.add_argument("--faiss", type=str, default=FAISS_PATH, help="Path to FAISS index")
    parser.add_argument("--meta", type=str, default=META_PATH, help="Path to metadata pickle")

    args = parser.parse_args()

    if not args.query:
        try:
            args.query = input("Enter query: ")
        except EOFError:
            print("No query provided. Exiting.")
            return

    try:
        answer = rag(args.query, top_k=args.top_k, faiss_path=args.faiss, meta_path=args.meta)
        print("\n=== Answer ===\n")
        print(answer)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
