from src.data_loader import load_all_documents
# from src.embeddings import EmbeddingPipeline
from src.vectorstore import FaissVectorStore
from src.search import RAGRetriever

#example usae

if __name__=="__main__":
    docs = load_all_documents("data")
    # store = FaissVectorStore("faiss_store")
    # store.build_from_documents(docs)

    # store.load()
    # print(store.query("Micro-Electro-Mechanical Systems (MEMS) Technologies", top_k=3))
    # rag_search = RAGRetriever()
    # query = "Security data preparing"
    # summary = rag_search.search_and_summarize(query, top_k=5)
    # print("Summary ==>>>", summary)
    # chunks = EmbeddingPipeline().chunk_documents(docs)
    # chunkvectors = EmbeddingPipeline().embed_documents(chunks)
    # print(chunkvectors)
    
    # print(f"Total documents loaded: {len(docs)}")
    # print(docs)

    ## Test Data Loader
    # docs = load_all_documents("data")
    # print(docs)
    
# if i had new document or reove one i had to run this to update the faiss index
    ## Test Embedding Pipeline
    # chunks = EmbeddingPipeline().chunk_documents(docs)
    # chunkvectors = EmbeddingPipeline().embed_documents(chunks)
    # print(chunkvectors)  

# but i use this inside the faiss function so i have  
# to call that only for now if any changes 
    store = FaissVectorStore("faiss_store")
    store.build_from_documents(docs)
    # just after i hace to call this to update the index
    store.load()
    #just for checking
    # print(store.query("Micro-Electro-Mechanical Systems (MEMS) Technologies", top_k=3))

    rag_search = RAGRetriever()
    query = "Security data preparing"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary ==>>>", summary)