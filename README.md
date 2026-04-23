# 🧠 AI Knowledge Assistant (Session-Isolated RAG)

Welcome to the **Question Answering System**, a professional-grade AI tool designed for research and technical inquiries. This system uses **RAG (Retrieval-Augmented Generation)** to answer questions based on a massive global database AND your own private documents.

---

## 🌟 Key Features

### 1. 📂 Personal Knowledge Upload (PDF)
You can upload any PDF or Research Paper. The AI will immediately "read" it and answer questions about it.
*   **Paperclip Icon:** Found directly in the chat bar for easy uploads.
*   **Table Reading:** Uses advanced processing to understand schedules, timings, and tables.

### 2. 🛡️ Private Chat Sessions (Session Isolation)
Your documents stay private. If you upload a PDF in "Chat A," the AI in "Chat B" will NOT know about it. Every conversation has its own "Private Brain."

### 3. 💾 Knowledge Persistence
Even if you close the app or restart your computer, the AI remembers the PDFs you uploaded for each chat.

### 4. ⚡ Dual Intelligence Mode
*   **Global Knowledge:** Searches a database of 600,000+ technical samples.
*   **Generative AI:** Uses local **Llama 3.2** to explain answers in natural, human language.

---

## 🚀 How to Run (Step-by-Step)

### 1. Start the AI Engine (Backend)
1.  Make sure **Ollama** is running on your computer.
2.  Open a terminal in the `backend/` folder.
3.  Run: `pip install -r requirements.txt`
4.  Run: `python app.py`

### 2. Start the Interface (Frontend)
1.  Open a second terminal in the `frontend/` folder.
2.  Run: `npm install`
3.  Run: `npm run dev`
4.  Open the link shown (usually `http://localhost:5173`).

---

## 🏗️ Technology Stack
*   **Backend:** FastAPI (Python), FAISS (Vector Database).
*   **AI Model:** Ollama (Llama 3.2:1b).
*   **Frontend:** React.js, Lucide Icons, Premium CSS.
*   **PDF Extraction:** pdfplumber.

---

## 📖 For Examiners (VIVA Prep)
This project demonstrates:
*   **Data Security:** By isolating vector indices per session.
*   **Scalability:** By using FAISS for lightning-fast retrieval.
*   **UX Design:** By implementing a modern, responsive, and intuitive interface.

---

Developed with ❤️ by **Yash Modi**
