from .indexer import Indexer
from .retriever import Retriever
from .generator import Generator

class RAGPipeline:
    def __init__(self):
        self.indexer = Indexer()
        # We initialize retriever lazily or handle its empty state gracefully
        self.retriever = None 
        self.generator = Generator()

    def initialize(self, reindex: bool = False):
        """Builds index if needed or requested."""
        self.indexer.build_index(force=reindex)
        # Reload retriever after potential indexing
        self.retriever = Retriever()

    def query(self, text: str, top_k: int = 5) -> str:
        if self.retriever is None:
             self.retriever = Retriever()
        
        results = self.retriever.search(text, top_k=top_k)
        
        # Deduplicate context based on text content to avoid repetition
        seen_texts = set()
        unique_results = []
        for r in results:
            if r['text'] not in seen_texts:
                seen_texts.add(r['text'])
                unique_results.append(r)

        context = "\n\n".join([r['text'] for r in unique_results])
        print(f"[INFO] Retrieved {len(unique_results)} relevant chunks.")
        
        answer = self.generator.generate_response(text, context)
        return answer
