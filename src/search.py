# from state import rag
from src.vectorstore import FaissVectorStore
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

# from langchain_google_genai import ChatGoogleGenerativeAI

class RAGRetriever:
    def __init__(self, persist_dir="faiss_store", embedding_model="all-MiniLM-L6-v2"):
        # if rag.loaded:
        #     return

        self.vector_store = FaissVectorStore(
            persist_dir=persist_dir,
            embedding_model=embedding_model
        )

        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from src.data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vector_store.build_from_documents(docs)
        else:
            self.vector_store.load()

        self.embedder = self.vector_store.model
        self.rag_retriever = self

    def search_and_summarize(self, query, top_k=5):
        results = self.vector_store.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]

        context = "\n\n".join(texts)

        if not context:
            return "No relevant context found."

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=1,
            max_tokens=799
        )

        prompt = f"""Use the following context to answer the question.


Context:
{context}

Question: {query}

Answer:"""

        response = llm.invoke(prompt)
        return response.content