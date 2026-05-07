# RAG — Retrieval-Augmented Generation Toolkit

Compact prototype and utilities for Retrieval-Augmented Generation (RAG). This repo contains scripts to embed documents, build and persist a FAISS vector store, run a small embedding server, and perform query-time retrieval + generative inference.

---

## Overview

This project demonstrates a simple RAG pipeline:
- Create dense embeddings for documents using SentenceTransformers.
- Store embeddings in a vector database (FAISS by default) and persist metadata separately.
- At query time, embed the query, retrieve top-k nearest passages from FAISS, and feed the retrieved context to a generative LLM to produce an answer.

The codebase is intentionally minimal to make it easy to prototype and adapt for experiments.

## Key files and folders

- `rag_run.py` — Minimal CLI: load FAISS + metadata, embed a query, retrieve top-k, and call the LLM.
- `server.py` / `client.py` — Tiny Flask embedding server and example client for embedding via HTTP.
- `indexer.py`, `index/`, `vector_store/`, `faiss_store/` — indexing helpers and places where FAISS index and metadata are stored (on-disk).
- `fast_rag/`, `src/` — local modules for pipeline pieces (embedding, retrieval, generator adapters).
- `requirements.txt` — Python dependencies (if present).
- `.gitignore` — configured to ignore model caches, vector store files, virtualenvs, and credentials.

If you add or change storage locations, update these paths consistently across scripts.

## Quickstart (local, PowerShell)

1. Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. If you want the embedding server (optional):
```powershell
python .\server.py
# Then from another shell you can POST text to http://localhost:5000/embed
```

3. Run a RAG query:
```powershell
python .\rag_run.py --query "What is retrieval augmented generation?" --top-k 3
```

4. Configure Google Generative API credentials (if using the Google LLM):
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS='C:\keys\rag-runner-key.json'
# or use gcloud for ADC:
gcloud auth application-default login
```

## Embeddings + FAISS notes (practical)

- Always convert embeddings to float32 for FAISS: `embs = np.asarray(embs, dtype='float32')`.
- If you want cosine similarity, normalize vectors with `faiss.normalize_L2(embs)` and use an IndexFlatIP index.
- For small corpora use IndexFlatL2/IndexFlatIP. For larger corpora consider IVF/HNSW/PQ indexes to reduce memory and speed up queries.
- Persist the FAISS index and metadata separately: `faiss.write_index(index, path)` and `pickle.dump(metadata_list, path)`.

Memory example: 384-dim vectors use ~384 * 4 = 1536 bytes per vector. 1M vectors ≈ 1.5GB.

## Single-package alternatives (embed + store together)

If you prefer a single system that stores vectors and metadata and provides queries, consider:

- Chroma (local-first, Python): simple, good for prototyping. Example snippet in repo docs.
- Qdrant (server): production-ready, gRPC/HTTP, payloads & filters.
- Weaviate, Milvus, Pinecone (hosted), pgvector (Postgres extension).

Example (Chroma) brief:
```python
from sentence_transformers import SentenceTransformer
import chromadb
client = chromadb.Client()
collection = client.get_or_create_collection('docs')
model = SentenceTransformer('all-MiniLM-L6-v2')
embs = model.encode(['a','b']).tolist()
collection.add(ids=['0','1'], documents=['a','b'], embeddings=embs)
```

## Troubleshooting

- "Your default credentials were not found": set `GOOGLE_APPLICATION_CREDENTIALS` or run `gcloud auth application-default login`.
- FAISS import issues on Windows: prefer `conda install -c pytorch faiss-cpu` or use a compatible wheel.
- High memory: load smaller models or use quantized/approximate indexes (IVF/HNSW/PQ).

## Next steps / how I can help

- Add a migration script to convert your FAISS store into Chroma/Qdrant.
- Add a startup log to `server.py`/`client.py` printing `__file__` and memory usage.
- Help purge leaked secrets from Git history (BFG/git-filter-repo) and coordinate a safe force-push.

---

If you want I can commit/format this README now, or tweak any section to include exact commands for your environment (Windows paths, service names). Which changes would you like? 
