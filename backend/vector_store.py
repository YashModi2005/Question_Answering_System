import faiss
import numpy as np
import pickle
import os
import glob

class VectorStore:
    def __init__(self, index_path=None, metadata_path=None, dimension=384):
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        # Define session directory relative to this file's location for portability
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.session_dir = os.path.join(current_dir, "sessions")
        
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
        
        # Main FAISS index for global knowledge
        if index_path and os.path.exists(index_path):
            print(f"Loading FAISS index from {index_path}...")
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            
        # Metadata for global knowledge
        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.metadata = []
            
        # Session-specific stores
        self.session_stores = {}
        self._load_session_stores()

    def _load_session_stores(self):
        """Loads any existing session indices from disk."""
        meta_files = glob.glob(os.path.join(self.session_dir, "*.pkl"))
        for meta_file in meta_files:
            session_id = os.path.basename(meta_file).replace(".pkl", "")
            index_file = meta_file.replace(".pkl", ".bin")
            
            if os.path.exists(index_file):
                try:
                    with open(meta_file, 'rb') as f:
                        meta = pickle.load(f)
                    idx = faiss.read_index(index_file)
                    self.session_stores[session_id] = {'index': idx, 'metadata': meta}
                    print(f"Loaded session store: {session_id} ({len(meta)} chunks)")
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")

    def add_embeddings(self, embeddings, documents):
        if not documents: return
        session_id = documents[0].get('session_id')
        
        if session_id:
            if session_id not in self.session_stores:
                self.session_stores[session_id] = {
                    'index': faiss.IndexFlatL2(self.dimension),
                    'metadata': []
                }
            store = self.session_stores[session_id]
            store['index'].add(embeddings)
            store['metadata'].extend(documents)
            self._save_session(session_id)
        else:
            self.index.add(embeddings)
            self.metadata.extend(documents)
            self.save() # Auto-save global changes

    def search(self, query_embedding: np.ndarray, top_k: int = 5, session_id: str = None):
        # FAISS requires a 2D array (N, dim). Ensure we have at least (1, dim)
        query_embedding = np.atleast_2d(query_embedding).astype('float32')
        query_embedding = np.ascontiguousarray(query_embedding)
        all_results = []

        # 1. Search Global Index
        if self.index.ntotal > 0:
            dist_g, idx_g = self.index.search(query_embedding, top_k)
            for j, idx in enumerate(idx_g[0]):
                if idx != -1 and idx < len(self.metadata):
                    all_results.append({"score": float(dist_g[0][j]), "document": self.metadata[idx]})

        # 2. Search Session Index (Strict Isolation & Priority)
        if session_id and session_id in self.session_stores:
            store = self.session_stores[session_id]
            if store['index'].ntotal > 0:
                s_k = min(top_k, store['index'].ntotal)
                dist_s, idx_s = store['index'].search(query_embedding, s_k)
                for j, idx in enumerate(idx_s[0]):
                    if idx != -1 and idx < len(store['metadata']):
                        all_results.append({"score": float(dist_s[0][j]), "document": store['metadata'][idx]})

        # Merge and take best top_k
        all_results.sort(key=lambda x: x['score'])
        return all_results[:top_k]

    def _save_session(self, session_id):
        """Saves a specific session store to disk."""
        if session_id in self.session_stores:
            store = self.session_stores[session_id]
            meta_path = os.path.join(self.session_dir, f"{session_id}.pkl")
            index_path = os.path.join(self.session_dir, f"{session_id}.bin")
            
            faiss.write_index(store['index'], index_path)
            with open(meta_path, 'wb') as f:
                pickle.dump(store['metadata'], f)

    def save(self):
        """Saves the global index."""
        if self.index_path:
            faiss.write_index(self.index, self.index_path)
        if self.metadata_path:
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
