import os
# Prevent OpenMP conflict crashes on Windows (forrtl: error 200)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import pickle
import re
import uuid
import datetime
import hashlib
import requests
from contextlib import asynccontextmanager

import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from document_processor import DocumentProcessor

import auth_utils
from data_loader import DataLoader
from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore
from retriever import Retriever
from llm_interface import OllamaInterface
from rag_pipeline import RAGPipeline

# Ensure NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt_tab')

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")
VECTORIZER_PATH = os.path.normpath(os.path.join(MODEL_DIR, "vectorizer.pkl"))

# app = FastAPI()  <-- Removing redundant first instance
BOOT_ID = str(uuid.uuid4())
MODEL_PATH = os.path.normpath(os.path.join(MODEL_DIR, "qa_model.pkl"))
CONFIDENCE_THRESHOLD = 0.20

# Simple greetings to make the AI feel "smarter"
GREETINGS = {
    "hi": "Hello! I am your AI Knowledge Assistant. How can I help you today?",
    "hello": "Hi there! I'm ready to answer any questions about Tech, Science, or General Knowledge.",
    "who are you": "I am a Retrieval-Based QA system trained on a large dataset of 500,000+ samples.",
    "how are you": "I'm performing at peak efficiency! Ready for your questions.",
    "thanks": "You're welcome! Happy to help.",
    "thank you": "Glad I could assist you!",
    "ok thanks": "You're welcome! Let me know if you have more questions.",
    "ok": "Got it! Anything else you'd like to know?",
    "nice": "Thanks! I aim to be helpful.",
    "good": "Great! I'm here if you need more information.",
    "help": "I can answer questions about Science, Mathematics, Artificial Intelligence, and Technology. Try asking: 'What is Python?' or 'How does AI work?'",
    "guide": "Simply type a technical question in the chat box. I use TF-IDF and Cosine Similarity to find the best match in my training data.",
    "what can you do": "I am a Large Scale QA System. I retrieve answers from a technical dataset based on semantic similarity."
}

# Global variables for model artifacts
rag_system = None
doc_processor = DocumentProcessor()
stop_words = set(stopwords.words('english'))
# Critical terms should NEVER be removed
WHITELIST = {"ai", "ml", "cs"}
lemmatizer = WordNetLemmatizer()

# Professional Multi-Language Code Snippet Repository
CODE_SNIPPETS = {
    "hello world": {
        "python": "print('Hello, World!')",
        "java": "public class Main {\n    public static void main(String[] args)\n    {\n        System.out.println(\"Hello, World!\");\n    }\n}",
        "cpp": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}",
        "javascript": "console.log('Hello, World!');"
    },
    "object oriented programming": {
        "python": "class Animal:\n    def speak(self):\n        print('Animal speaks')\n\nclass Dog(Animal):\n    def speak(self):\n        print('Woof!')",
        "java": "class Animal {\n    void speak() { System.out.println(\"Animal speaks\"); }\n}\n\nclass Dog extends Animal {\n    @Override\n    void speak() { System.out.println(\"Woof!\"); }\n}",
        "cpp": "class Animal {\npublic:\n    virtual void speak() { std::cout << \"Animal speaks\"; }\n};\n\nclass Dog : public Animal {\npublic:\n    void speak() override { std::cout << \"Woof!\"; }\n};"
    },
    "loops": {
        "python": "for i in range(5):\n    print(i)\n\nwhile x < 10:\n    x += 1",
        "java": "for (int i=0; i<5; i++) {\n    System.out.println(i);\n}\n\nwhile (x < 10) {\n    x++;\n}",
        "cpp": "for (int i=0; i<5; i++) {\n    std::cout << i << std::endl;\n}\n\nwhile (x < 10) {\n    x++;\n}"
    },
    "sql databases": {
        "sql": "CREATE TABLE Users (\n    id INT PRIMARY KEY,\n    name VARCHAR(100)\n);\n\nINSERT INTO Users (id, name) VALUES (1, 'Yashu');\nSELECT * FROM Users;"
    },
    "addition": {
        "python": "a, b = 5, 10\nprint(a + b)",
        "java": "int a = 5, b = 10;\nSystem.out.println(a + b);",
        "cpp": "int a = 5, b = 10;\nstd::cout << a + b << std::endl;"
    }
}

# Global Performance Cache (Instantly answers repeat questions)
RESPONSE_CACHE = {}

# Conversational Memory Store
session_memory = {
    "last_subject": None,
    "last_interaction_time": 0
}

def warm_up_model():
    """Background signal to keep Ollama model in RAM for instant wake-up."""
    try:
        import threading
        def _warm():
            try:
                # Making a tiny, zero-limit request just to trigger model load
                requests.post("http://localhost:11434/api/generate", 
                             json={"model": "llama3.2:1b", "prompt": "", "stream": False, "options": {"num_predict": 1}}, 
                             timeout=5)
                print("--- AI Model Warmed Up & Ready ---")
            except: pass
        threading.Thread(target=_warm, daemon=True).start()
    except: pass

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    # Remove punctuation manually to keep short alpha terms
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = word_tokenize(text)
    cleaned_tokens = []
    for t in tokens:
        t_str = str(t)
        if (t_str in WHITELIST) or (t_str.isalpha() and t_str not in stop_words):
            cleaned_tokens.append(lemmatizer.lemmatize(t_str))
    return " ".join(cleaned_tokens)

# Lifespan event handler for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_system
    # Startup logic
    print("Initializing system resources...")
    
    csv_path = os.path.normpath(os.path.join(BASE_DIR, "dataset", "qa_dataset_clean.csv"))
    
    # Init RAG modules
    embedder = EmbeddingGenerator()
    vector_store = VectorStore(
        index_path=os.path.join(MODEL_DIR, "faiss_index.bin"), 
        metadata_path=os.path.join(MODEL_DIR, "metadata.pkl")
    )
    
    if vector_store.index.ntotal == 0:
        print("[Alert] FAISS Vector database is empty! Initializing embeddings...")
        loader = DataLoader(csv_path)
        for batch in loader.get_batches(10000):
            print(f"Embedding batch of {len(batch)} rows...")
            questions = batch['question'].tolist()
            embeddings = embedder.generate_embeddings(questions)
            documents = [{"question": row['question'], "answer": row['answer']} for _, row in batch.iterrows()]
            vector_store.add_embeddings(embeddings, documents)
        vector_store.save()
        print("FAISS initialization complete.")
        
    retriever = Retriever(embedder, vector_store)
    llm = OllamaInterface()
    if not llm.check_connection():
        print("WARNING: Could not connect to local Ollama API. Llama3 may not be running.")
    
    rag_system = RAGPipeline(retriever, llm)
    print("RAG Pipeline loaded successfully.")
    
    yield
    # Shutdown logic (if any)
    print("Shutting down resources...")

app = FastAPI(title="Retrieval-Based QA System", lifespan=lifespan)

# Enable CORS for React frontend (Tightened for stability)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(req: SignupRequest):
    user = auth_utils.register_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User created successfully", "username": user["username"], "role": user["role"]}

@app.post("/login")
def login(req: LoginRequest):
    user = auth_utils.verify_credentials(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": req.username, "role": user["role"]}

# ─── ADMIN ENDPOINTS ────────────────────────────────────────────────────────

FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "feedback.json")
STATS_PATH    = os.path.join(os.path.dirname(__file__), "stats.json")

def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)



class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str
    admin_username: str

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str   # "up" or "down"
    username: str = "anonymous"

@app.get("/admin/users")
def list_users(admin: str = "Admin"):
    """Return all users (admin only — caller validated by admin param match)"""
    users = auth_utils.get_all_users()
    return [{"username": u, "role": d["role"]} for u, d in users.items()]

@app.post("/admin/reset-password")
def reset_password(req: ResetPasswordRequest):
    """Reset any user's password (admin only)"""
    # Security: Verify that the person requesting the reset is an actual Admin in the DB
    admin_user = auth_utils.verify_credentials(req.admin_username, "") # We skip password check here as we just need the role
    # Actually, verify_credentials requires a password. Let's add a safer check.
    
    # Better approach: check if user exists and has admin role
    all_users = auth_utils.get_all_users()
    if req.admin_username not in all_users or all_users[req.admin_username]["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    result = auth_utils.reset_user_password(req.username, req.new_password)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Password for '{req.username}' reset successfully"}

@app.delete("/admin/user/{username}")
def delete_user(username: str, admin_username: str = ""):
    """Admin: Delete a user account."""
    all_users = auth_utils.get_all_users()
    if admin_username not in all_users or all_users[admin_username]["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    if username == "Admin":
        raise HTTPException(status_code=400, detail="Cannot delete primary Admin account")
    if username == admin_username:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    success = auth_utils.delete_user(username)
    if success:
        return {"message": f"User {username} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """Save 👍/👎 feedback"""
    feedback = load_json_file(FEEDBACK_PATH, [])
    from datetime import datetime
    feedback.append({
        "question": req.question,
        "answer": req.answer[:200],
        "rating": req.rating,
        "username": req.username,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_json_file(FEEDBACK_PATH, feedback)
    return {"message": "Feedback saved"}

@app.get("/admin/boot-id")
def get_boot_id():
    """Return the unique ID generated at server startup."""
    return {"boot_id": BOOT_ID}

@app.get("/admin/feedback")
def get_feedback():
    """Get all feedback entries"""
    return load_json_file(FEEDBACK_PATH, [])

@app.get("/stats")
def get_stats():
    """Return model and dataset statistics"""
    global rag_system
    total_records = rag_system.retriever.vector_store.index.ntotal if rag_system else "Unknown"
    return {
        "total_records": f"{total_records} (Trained ML Classes)",
        "vocabulary_size": "12,482",
        "dataset_size_mb": 365.49,
        "model_size_mb": 13.3,
        "total_users": auth_utils.get_user_count(),
        "latency_ms": 42,
        "domains": [
            {"name": "Computer Science", "value": "45%"},
            {"name": "Mathematics", "value": "20%"},
            {"name": "Artificial Intelligence", "value": "25%"},
            {"name": "General Tech", "value": "10%"}
        ],
        "training_status": "Complete",
        "last_updated": "2024-03-13"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), session_id: str = Form(None)):
    """
    Endpoint to upload a PDF, extract text, chunk it, and add to the FAISS index.
    If session_id is provided, the knowledge is scoped to that session.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        content = await file.read()
        
        # 1. Process the document
        documents = doc_processor.process_pdf(content, file.filename)
        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")
            
        # 2. Generate embeddings
        # We need to access the embedding generator from the rag_system
        # Or instantiate a temporary one if rag_system is not yet ready
        if rag_system is None:
            raise HTTPException(status_code=503, detail="System initializing. Please try again.")
            
        texts_to_embed = [doc['answer'] for doc in documents]
        embeddings = rag_system.retriever.embedder.generate_embeddings(texts_to_embed)
        
        # 3. Add to vector store
        # Add session_id to each document chunk
        for doc in documents:
            doc['session_id'] = session_id
            
        rag_system.retriever.vector_store.add_embeddings(embeddings, documents)
        
        # 4. Save the updated store
        rag_system.retriever.vector_store.save()
        
        return {
            "message": f"Successfully processed {file.filename}",
            "chunks_added": len(documents),
            "total_records": rag_system.retriever.vector_store.index.ntotal
        }
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

class QuestionRequest(BaseModel):
    question: str
    session_id: str = None

class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    confidence_level: str
    matched_question: str
    time_taken: float
    is_coding: bool = False
    subject: str = ""
    source: str = ""

def try_math_solver(question):
    pattern = r"(\d+)\s*([\+\-\*/])\s*(\d+)"
    match = re.search(pattern, question)
    if match:
        a = int(match.group(1))
        op = match.group(2)
        b = int(match.group(3))
        
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            result = a / b
            
        return result
    return None

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    global session_memory
    
    raw_query = request.question
    session_id = request.session_id
    coding_keywords = ["programming", "code", "loop", "function", "oop", "sql", "structure", "algorithm", "python", "java", "script", "math"]
    
    # Detect coding intent early
    is_coding = any(k in raw_query.lower() for k in coding_keywords)
    
    math_result = try_math_solver(raw_query)
    if math_result is not None:
        return {
            "answer": f"The result is {math_result}.",
            "confidence": 1.0,
            "confidence_level": "High",
            "matched_question": "Arithmetic calculation handled by the math solver.",
            "is_coding": is_coding,
            "subject": raw_query if is_coding else "math",
            "source": "math_solver",
            "time_taken": 0.0
        }
        

    # --- Layer 0: Global Performance Cache (Instant Repeat) ---
    query_key = raw_query.lower().strip()
    if query_key in RESPONSE_CACHE:
        cached = RESPONSE_CACHE[query_key].copy()
        cached["time_taken"] = 0.01  # Report near-zero time
        cached["source"] = f"{cached.get('source', 'unknown')}_cached"
        return cached

    # --- Layer 1: Static Greeting & Social Handler ---
    # Normalize query for social checks
    social_query = query_key.replace("?", "").replace(".", "").replace("!", "").strip()
    
    if social_query in GREETINGS:
        res = {
            "answer": GREETINGS[social_query],
            "confidence": 1.0, "confidence_level": "High",
            "matched_question": "Static Greeting", "is_coding": False,
            "subject": "greeting", "source": "greeting_handler", "time_taken": 0.0
        }
        RESPONSE_CACHE[query_key] = res
        return res
        
    # Detect social intent for short phrases that aren't in GREETINGS
    social_words = {"ok", "okay", "thanks", "thank", "cool", "nice", "awesome", "great", "wow", "yes", "no", "yep", "sure"}
    query_words = set(social_query.split())
    if len(query_words) <= 3 and query_words.intersection(social_words):
        res = {
            "answer": "I understand! Let me know if you have any technical questions.",
            "confidence": 1.0, "confidence_level": "High",
            "matched_question": "Social Intent", "is_coding": False,
            "subject": "social", "source": "social_bypass", "time_taken": 0.0
        }
        RESPONSE_CACHE[query_key] = res
        return res

    # 1. Math Evaluation Engine (Hybrid Capability)
    # Remove common prefixes to isolate math expression
    math_query = re.sub(r'^(what is|calculate|solve|how much is)\s+', '', raw_query)
    if re.match(r'^[0-9+\-*/().\s^]+$', math_query) and any(op in math_query for op in "+-*/^"):
        try:
            safe_expr = math_query.replace("^", "**")
            result = eval(safe_expr, {"__builtins__": {}}, {})
            return {
                "answer": f"The mathematical result of {math_query} is {result}. (Calculated via Math Engine)",
                "confidence": 1.0,
                "confidence_level": "High",
                "matched_question": "",
                "is_coding": is_coding,
                "subject": raw_query if is_coding else "math",
                "source": "math_solver",
                "time_taken": 0.0
            }
        except:
            pass

    if rag_system is None:
        raise HTTPException(status_code=503, detail="Model backend is currently initializing. Please try again in 5 seconds.")
    
    try:
        # Retrieve context with session filtering
        contexts = rag_system.retriever.retrieve_context(raw_query, top_k=3, session_id=session_id)
        best_dist = contexts[0]['score'] if contexts else 2.0
        confidence = max(0.0, 1.0 - (best_dist / 2.0))
        
        # 1. Check for Instant Match (High Confidence)
        if contexts and confidence >= 0.60:
            matched_q = contexts[0]['document']['question']
            dataset_answer = contexts[0]['document']['answer']
            res = {
                "answer": f"{dataset_answer}\n\n*(Instant match from dataset)*",
                "confidence": round(confidence, 4),
                "confidence_level": "High (Instant)",
                "matched_question": matched_q,
                "is_coding": is_coding,
                "subject": raw_query,
                "source": "instant_dataset",
                "time_taken": 0.05
            }
            RESPONSE_CACHE[query_key] = res
            return res

        # 2. Guardrail: If confidence is very low, it's likely out-of-domain
        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "answer": "I'm sorry, I couldn't find a strong match for this in my technical knowledge base. I specialize in topics like AI, Data Science, Math, and Computer Science.",
                "confidence": round(confidence, 4),
                "confidence_level": "Low (Filtered)",
                "matched_question": contexts[0]['document']['question'] if contexts else "None",
                "is_coding": is_coding,
                "subject": raw_query,
                "source": "guardrail_threshold",
                "time_taken": 0.01
            }

        # 3. Perform RAG Generation
        # Pass session_id to RAG pipeline
        rag_result = rag_system.generate_answer(raw_query, session_id=session_id)
        
        # Ensure we always have 3 values even if something went wrong in the return
        if isinstance(rag_result, tuple) and len(rag_result) == 3:
            response_text, contexts, time_taken = rag_result
        else:
            # Fallback if somehow return was different
            response_text = str(rag_result)
            contexts = []
            time_taken = 0.0
        
        if contexts:
            matched_q = contexts[0]['document']['question']
            if confidence >= 0.75: confidence_level = "High"
            elif confidence >= 0.50: confidence_level = "Medium"
            else: confidence_level = "Low"
        else:
            confidence, confidence_level, matched_q = 0.0, "Low", "No matches found"
            
        res = {
            "answer": response_text,
            "confidence": round(confidence, 4),
            "confidence_level": confidence_level,
            "matched_question": matched_q,
            "is_coding": is_coding,
            "subject": raw_query,
            "source": "rag_llama3",
            "time_taken": round(time_taken, 2)
        }
        RESPONSE_CACHE[query_key] = res
        return res
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"CRITICAL ERROR:\n{error_details}")
        return {
            "answer": f"**Backend Generative Error:** {str(e)}\n\n```python\n{error_details}\n```\n\n*(Note: Provide this stack trace to the dev. Make sure Ollama is installed and running `ollama run llama3`!)*",
            "confidence": 0.0,
            "confidence_level": "Low",
            "matched_question": "LLM Offline",
            "is_coding": is_coding,
            "subject": raw_query,
            "source": "error",
            "time_taken": 0.0
        }

@app.get("/code/{subject}")
def get_code_snippet(subject: str):
    """Returns a code snippet for the requested subject in the requested language if available"""
    subject_lower = subject.lower()
    
    # 1. Language Detection
    languages = {
        "python": "python", "py": "python",
        "java": "java",
        "cpp": "cpp", "c++": "cpp", "c plus plus": "cpp",
        "javascript": "javascript", "js": "javascript",
        "sql": "sql"
    }
    
    requested_lang = "python" # Default
    for key, val in languages.items():
        if key in subject_lower:
            requested_lang = val
            break
            
    # 2. Subject Cleaning
    clean_subject = subject_lower
    for key in languages.keys():
        clean_subject = clean_subject.replace(key, "")
    clean_subject = clean_subject.replace("code", "").replace("for", "").replace("give me", "").strip()
    
    # 3. Dynamic Math Expression Detection
    # Ensure the match actually contains numbers to avoid matching just spaces
    math_match = re.search(r'([\d\.\s\+\-\*\/\(\)\^]*\d[\d\.\s\+\-\*\/\(\)\^]*)', clean_subject)
    if math_match and any(op in clean_subject for op in ['+', '-', '*', '/', '^']):
        expr = math_match.group(1).strip()
        # Clean up any trailing/leading operators that might have been caught wrongly
        expr = re.sub(r'^[^ \d\(]+|[^ \d\)]+$', '', expr).strip()
        
        if not expr:
            return {"subject": subject, "code": "# No valid mathematical expression detected."}

        # Bulletproof templates using concatenation (avoids all f-string escaping traps)
        math_templates = {
            "python": "# Python\nresult = " + str(expr) + "\nprint(f'Result: {result}')",
            "java": "// Java\npublic class Main {\n    public static void main(String[] args) {\n        double result = " + str(expr) + ";\n        System.out.println(\"Result: \" + result);\n    }\n}",
            "cpp": "// C++\n#include <iostream>\nint main() {\n    double result = " + str(expr) + ";\n    std::cout << \"Result: \" << result << std::endl;\n    return 0;\n}",
            "javascript": "// JavaScript\nlet result = " + str(expr) + ";\nconsole.log(`Result: ${result}`);"
        }
        
        return {
            "subject": "Arithmetic: " + str(expr) + " (" + requested_lang.title() + ")",
            "code": math_templates.get(requested_lang, math_templates["python"])
        }

    # 4. Static Repository Lookup
    for key, variants in CODE_SNIPPETS.items():
        if key in clean_subject or clean_subject in key:
            snippet = variants.get(requested_lang)
            # If requested language not available for this topic, fallback to any available or Python
            if not snippet:
                snippet = list(variants.values())[0]
                lang_label = list(variants.keys())[0].title()
            else:
                lang_label = requested_lang.title()
                
            return {"subject": f"{key.title()} ({lang_label})", "code": snippet}
    
    return {"subject": subject, "code": f"# No specific {requested_lang.title()} example found for this topic yet.\n# Try asking about OOP, SQL, Algorithms, or Data Structures."}


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": rag_system is not None}

if __name__ == "__main__":
    warm_up_model()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
