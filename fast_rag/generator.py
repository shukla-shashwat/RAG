from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .config import GENERATION_MODEL

load_dotenv()

class Generator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=GENERATION_MODEL,
            temperature=0.7, # Slightly lower temperature for more focused answers
            max_tokens=1024,
            timeout=30,
            max_retries=2,
        )

    def generate_response(self, query: str, context: str) -> str:
        if not context:
            return "I couldn't find any relevant information in the documents to answer your question."

        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.
If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating response: {e}"
