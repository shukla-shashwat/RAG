import time
# Timer helper
def t():
    return time.perf_counter()
start_total = t()
# import faiss
# import pickle
# from langchain_google_genai import ChatGoogleGenerativeAI
t10 = t()
import requests
import numpy as np
# import re
from dotenv import load_dotenv
# from server import embed
# from client import faiss, meta, chat 
load_dotenv()
t9 = t()
t0 = t()


# Fixed config paths
# FAISS_PATH = "faiss_store/faiss.index"
# META_PATH = "faiss_store/metadata.pkl"
# EMBED_MODEL = "all-MiniLM-L6-v2"

# Fixed query text (hardcoded)
QUERY = "A multi-layered framework for smart cybersecurity services"
query = QUERY
# Load FAISS index
# index = faiss(FAISS_PATH)
# Load metadata
t1 = t()
# with open(META_PATH, "rb") as f:
#     metadata = pickle.load(f)
# metadata = meta(META_PATH)

# Load embedding model
t2 = t()
# model = SentenceTransformer(EMBED_MODEL)

# Embed the fixed query
t3 = t()
def embed(text: str) -> np.ndarray:
    raw = requests.post("http://localhost:5000/embed", data=text).json()

    # Extract only valid numbers
    # numbers = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", raw)

    # if not numbers:
    #     print("ERROR FROM SERVER:\n", raw)
    #     raise ValueError("Server returned invalid output instead of embedding.")

    # floats = [float(x) for x in numbers]

    # floats = floats[:384]

    # return np.array([floats], dtype="float32")
    arr = np.array(raw, dtype="float32")

    print("Embedding shape:", arr.shape)   # Debug shape
    return arr
query_embedding = embed(QUERY)
# query_embedding = model
#.encode([QUERY]).astype("float32")

# Perform FAISS search
t4 = t()
# distances, indices = index.search(query_embedding, 3)
faiss_response = requests.post(
    "http://localhost:5001/faiss",
    json={
        "embedding": query_embedding[0].tolist(),
        "top_k": 3
    }
).json()

# print()
# for item in faiss_response:
#     print(item["text"])
#     print("\n-------------------------------------------------------------")
# Print retrieved context chunks
t5  = t()
context = "\n\n".join([item["text"] for item in faiss_response])

# for idx in indices[0]:
#     print(metadata[idx]["text"])
#     print()
#     print("-------------------------------------------------------------")

t6 = t()
prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {query}

Answer:"""
# llm = chat()
chat_response = requests.post(
    "http://localhost:5001/chat",
    json={"prompt": prompt}
).json()
t7 = t()
# todo
# /* makea chatbot in which i have to make this code in which i send the uery and it give the output but here is the context that for achieve that it alway get my rag.py run from starting rather it doesn,t have any change */
# and i hve the system of in memory procesing not persistent so if anyne want to chane the file at the time of query it take so much time to do everyhing from scratch which tend my system is not scalable and for good for production
# what i think that tel me which i smore approprate for make this rag faster i have thus as priority i dont have feeling about my memoery i just want to make this rag fat so which is more reliable for my use case in memory and persistance storae working an alo if anyone change anything at the time of run state in the dataset like add onr pdf so it dont have to make the vector for whle db but only for that pdf and append it in my vector db 

    
# context = "\n\n".join([metadata[idx]["text"] for idx in indices[0]])
# prompt = f"""Use the following context to answer the question.


# Context:
# {context}

# Question: {query}

# Answer:"""

# response = llm.invoke(prompt)
# print(f""" LLM OUTPUT ->>> {response.content}""")


answer = chat_response["answer"]
print(f"""\nLLM OUTPUT ->>> {answer}""")
t8 = t()
print(f"\nTotal time: {t() - start_total:.4f} sec")
print(f"Embed query: {t4 - t3:.4f} sec")
print(f"Load FAISS index: {t5 - t4:.4f} sec")
print(f"Prepare context: {t6 - t5:.4f} sec")
print(f"Generate response: {t7 - t6:.4f} sec")
# print(f"Load metadata: {t2 - t1:.4f} sec")
# print(f"Load embedding model: {t3 - t2:.4f} sec")
# print(f"FAISS search: {t5 - t4:.4f} sec")
print(f"import overhead: {t9 - t10:.4f} sec")
# print(f"server overhead: {t10 - t9:.4f} sec")