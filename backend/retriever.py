from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore

class Retriever:
    """
    Coordinates the translation of string queries into embeddings, 
    and searching the vector database for matching records.
    """
    def __init__(self, embedder: EmbeddingGenerator, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
        
    def retrieve_context(self, query_text: str, top_k: int = 5, session_id: str = None) -> list[dict]:
        """
        Embeds the query and fetches top-k results from vector store.
        """
        query_vector = self.embedder.generate_embeddings([query_text])
        return self.vector_store.search(query_vector, top_k=top_k, session_id=session_id)
