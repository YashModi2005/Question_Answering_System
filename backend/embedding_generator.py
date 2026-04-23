from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    """
    Handles generating dense vector embeddings for text using SentenceTransformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Initializing SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Converts a list of string texts into a numpy array of embeddings.
        We return as float32 which is the standard format required by FAISS.
        """
        # Set show_progress_bar=False to avoid spamming logs when running in batches
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # Ensure the embeddings are typed as float32 for FAISS L2 indexing
        return np.array(embeddings).astype('float32')

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single question query to match against the database.
        Returns a 2D array (1, vector_dimension) for FAISS searching.
        """
        embedding = self.model.encode([query], convert_to_numpy=True)
        return np.array(embedding).astype('float32')
