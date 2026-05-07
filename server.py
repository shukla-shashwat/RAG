from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify

model = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)

@app.route("/embed", methods=["POST"])
def embed():
    # text = request.json["text"]
    # emb = model.encode([text]).astype("float32")
    # return (emb)
    text = request.data.decode()
    emb = model.encode([text]).astype("float32")
    return jsonify(emb.tolist())

if __name__ == "__main__":
    print("Model loaded. Server running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
