# 🚀 Technical Viva Study Guide (Simple Language)

This guide explains how your **Technical Knowledge Assistant** works. Study this for your oral exam!

---

### 1. How was the Dataset generated?
We used a Python script (`generate_dataset.py`) to automatically build a technical library.
*   **Source**: It uses the **Wikipedia API** to fetch summaries of technical topics (e.g., "What is a Kernel?").
*   **Logic**: It takes those summaries and generates **7 different variations** of questions for each topic (e.g., "Define X", "Explain X", "What is X?").
*   **Scale**: Your database now contains over **600,000 records** of high-quality technical knowledge.

### 2. Which Models are you using?
Your project uses TWO different AI models working together:
1.  **Sentence-Transformers (`all-MiniLM-L6-v2`)**: This is the "Searcher." It converts your text into a list of numbers (Vectors) so the computer can find similar questions using math.
2.  **Ollama Llama 3.2**: This is the "Brain." It reads the context we found and writes a natural, human-like answer for the user.

### 3. How does the Information Flow? (Step-by-Step)
1.  **Frontend (UI)**: You type a question in the React app.
2.  **Request**: React sends a `POST` request to the FastAPI **Backend**.
3.  **Search**: The backend turns your question into a "Vector" and searches the **FAISS Database** to find the closest matching answer.
4.  **Generation**: The backend sends the question + the found context to the **Llama 3 AI model**.
5.  **Response**: The AI generates a clear answer, and the backend sends it back to the Frontend (React) to show it to you.

### 4. How does the Microphone work?
We use the **Web Speech API** (`webkitSpeechRecognition`) built into the browser. 
*   It listens to your voice via the microphone.
*   It converts your audio "on-the-fly" into text (Speech-to-Text).
*   The text is then automatically typed into the chat box for you.

### 5. Why is it called "RAG"?
**RAG** stands for **Retrieval-Augmented Generation**.
*   **Retrieval**: We "Retrieve" (find) the facts from our own local database.
*   **Augmented**: We "Augment" (add) those facts to the AI's prompt.
*   **Generation**: The AI "Generates" a final answer based on those local facts.

---

### 🔥 Top 3 "Killer" Questions & Answers for Examiners:
*   **Q: Why not just use ChatGPT directly?**
    *   **A**: *"My system is private and uses a local database. It doesn't need the internet to find answers, and it only uses validated technical data, so it avoids 'hallucinations' better than basic AI."*
*   **Q: What is FAISS?**
    *   **A**: *"FAISS is a library created by Meta. It allows us to search through millions of pieces of data in milliseconds by comparing the 'distance' between vectors (math numbers)."*
*   **Q: Why is your system 'Intelligent'?**
    *   **A**: *"Because it doesn't just look for exact words. It looks for the 'semantic meaning' (intended meaning) of the question, so even if you make a small typo, it still understands you!"*
