import os
import sys
import datetime
from data_loader import DataLoader
from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore
from retriever import Retriever
from llm_interface import OllamaInterface
from rag_pipeline import RAGPipeline

LOG_FILE = "query_logs.txt"

def log_interaction(question: str, response: str):
    """
    Logs user queries and system responses to a text file.
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now().isoformat()}]\n")
        f.write(f"User Question: {question}\n")
        f.write(f"AI Response: {response[:100]}...\n") # Log preview
        f.write("-" * 50)

def initialize_system(csv_path: str, batch_size: int = 10000) -> RAGPipeline:
    """
    Bootstraps the entire modular system. If the FAISS database is empty,
    it automatically triggers the 600K row batching embedding payload.
    """
    embedder = EmbeddingGenerator()
    vector_store = VectorStore()
    
    # Check if the FAISS index needs to be (re)built
    if vector_store.index.ntotal == 0:
        print("\n[Alert] Vector database is entirely empty!")
        print(f"Initializing embedding pipeline from {csv_path}...")
        loader = DataLoader(csv_path)
        
        batch_count = 1
        for batch in loader.get_batches(batch_size):
            print(f"Embedding batch {batch_count} ({len(batch)} rows)...")
            questions = batch['question'].tolist()
            embeddings = embedder.generate_embeddings(questions)
            
            # Format metadata
            documents = [{"question": row['question'], "answer": row['answer']} for _, row in batch.iterrows()]
            
            vector_store.add_embeddings(embeddings, documents)
            batch_count += 1
            
            # Save incrementally just in case we hit a local memory abort midway
            vector_store.save()
            
        print("\nFinished converting all datatset vectors!")
        vector_store.save()
    
    retriever = Retriever(embedder, vector_store)
    llm = OllamaInterface()
    
    # Warm up validation warning
    if not llm.check_connection():
        print("\n===============================")
        print("WARNING: Could not connect to local Ollama API.")
        print("Please make sure Ollama is installed and running `ollama run llama3` in another terminal!")
        print("===============================\n")
        
    return RAGPipeline(retriever, llm)

def main():
    # Attempting to track down the absolute path of the user's old dataset
    desktop_dir = os.path.dirname(os.path.abspath(__file__))
    # CORRECT PATH: desktop_dir is backend/, so .. is project root. Then go into dataset/
    csv_path = os.path.join(desktop_dir, "..", "dataset", "qa_dataset_clean.csv")
    csv_path = os.path.normpath(csv_path)
    
    if not os.path.exists(csv_path):
        print(f"Error: Could not locate dataset at {csv_path}")
        print("Please place 'qa_dataset_clean.csv' in the local directory or update the script path.")
        sys.exit(1)
        
    pipeline = initialize_system(csv_path)
    
    print("\n" + "="*50)
    print("  🚀 Llama 3 RAG Knowledge Assistant Online  ")
    print("="*50)
    print("Type 'quit' or 'exit' to stop the engine.\n")
    
    while True:
        try:
            query = input("User Question > ")
            if query.lower() in ['quit', 'exit']:
                print("Shutting down engine...")
                break
            
            if not query.strip():
                continue
                
            print("\nSearching Memory Database & Streaming to LLM...")
            # Retrieve answer string and context metadata payload 
            response, contexts = pipeline.generate_answer(query)
            
            print("\n" + "="*50)
            print("🤖 AI Response:")
            print(response)
            print("="*50)
            
            print("\n[Retrieved Context Metadata]")
            for i, ctx in enumerate(contexts):
                score = ctx['score']
                doc = ctx['document']
                # Lower FAISS L2 score means closer/better match
                print(f"-> Source {i+1} | Diff Score: {score:.3f} | Matched Q: {doc['question']}")
                
            print("\n" + "-"*50 + "\n")
            
            # Log the successful interaction locally
            log_interaction(query, response)
            
        except KeyboardInterrupt:
            print("\nEngine interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred during generative inference: {e}\n")

if __name__ == "__main__":
    main()
