
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from db_config import get_db_connection
    conn = get_db_connection()
    if conn:
        print("DB Connection: SUCCESS")
        conn.close()
    else:
        print("DB Connection: FAILED")
except Exception as e:
    print(f"DB Connection Error: {e}")

try:
    import faiss
    import pickle
    
    index_path = os.path.join('model', 'faiss_index.bin')
    if os.path.exists(index_path):
        print(f"Checking index: {index_path}")
        index = faiss.read_index(index_path)
        print(f"FAISS Index Load: SUCCESS (Total: {index.ntotal})")
    else:
        print(f"FAISS Index: NOT FOUND at {index_path}")
except Exception as e:
    print(f"FAISS Error: {e}")

try:
    import requests
    res = requests.get("http://localhost:11434/api/tags", timeout=2)
    print(f"Ollama Status: SUCCESS ({res.status_code})")
except Exception as e:
    print(f"Ollama Status: FAILED ({e})")
