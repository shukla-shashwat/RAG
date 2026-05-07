from flask import Flask, request, jsonify
import faiss
import pickle
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

FAISS_PATH = "faiss_store/faiss.index"
META_PATH = "faiss_store/metadata.pkl"

# Load heavy stuff once
index = faiss.read_index(FAISS_PATH)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=1,
    max_tokens=299
)

app = Flask(__name__)

@app.route("/faiss", methods=["POST"])
def faiss_search():
    """Body: { "embedding": [...], "top_k": 3 }"""
    data = request.get_json()
    embedding = np.array([data["embedding"]], dtype="float32")
    top_k = int(data.get("top_k", 3))

    D, I = index.search(embedding, top_k)

    results = []
    for idx, dist in zip(I[0], D[0]):
        chunk_text = metadata[idx]["text"]
        results.append({
            "index": int(idx),
            "distance": float(dist),
            "text": chunk_text,
        })

    return jsonify(results)

@app.route("/chat", methods=["POST"])
def chat():
    """Body: { "prompt": "...." }"""
    data = request.get_json()
    prompt = data["prompt"]

    res = llm_model.invoke(prompt)
    return jsonify({"answer": res.content})

if __name__ == "__main__":
    print("FAISS + LLM server running at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
