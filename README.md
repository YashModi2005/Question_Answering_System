# AI-Powered Technical Question Answering System

A professional Retrieval-Augmented Generation (RAG) system specializing in Technical Knowledge, Science, and Computer Science. This project features a **FastAPI backend** paired with a **React (Vite) frontend**, using **TF-IDF Vectorization**, **FAISS Vector Store**, and **Llama 3.2 (via Ollama)** for intelligent response generation.

---

## 🛠️ Step-by-Step Setup Instructions

### 1. Prerequisites
- **Python 3.8+**
- **Node.js & npm**
- **MySQL Server**
- **Ollama** (for AI generation)
  - Install Ollama and run: `ollama pull llama3.2:1b` (or 3b)

### 2. Database Preparation (Critical)
Before running the application, you must initialize the MySQL database and migrate the user credentials.

```bash
# Navigate to the backend directory
cd backend

# 1. Create the database 'qa_system' and tables
python setup_mysql.py

# 2. Migrate default users (Admin/Yash) to the database
python migrate_users.py
```

### 3. Start the Backend (Web Server)
To use the browser-based chat interface, start the FastAPI server:
```bash
# From the project root or backend folder
python backend/app.py
```
*The API will be live at `http://localhost:8000`.*

### 4. Start the Frontend (Vite)
Open a new terminal and run:
```bash
cd frontend
npm install   # Run once to install dependencies
npm run dev
```
*Access the UI at the URL provided (default: `http://localhost:5173`).*

---

## 📊 Data Generation & Pipeline

### 1. Synthetic Dataset Synthesis
The core of this project is a massive, high-quality technical dataset synthesized using a custom **Domain-Specific Fact Engine**.

- **Scale**: 600,000+ unique Question-Answer pairs.
- **Domains (11 Categories)**: Artificial Intelligence, Machine Learning, NLP, Operating Systems, Databases, Networking, Algorithms, CS Fundamentals, and more.
- **Generation Logic**: Uses 50+ core technical concepts combined with a permutation engine of 16 syntax templates to ensure linguistic variety.
- **Noise Injection**: 1% randomized noise (contextual variations) is included to challenge the AI's retrieval performance.

### 2. Cleaning & Normalization
To ensure high-quality retrieval, the raw data undergoes a strict automated cleaning pipeline:
- **Duplicate Removal**: Eliminates redundant questions to keep the FAISS index lean.
- **Length Filtering**: Ensures answers are comprehensive (minimum 15-word requirement).
- **Normalization**: Standardizes whitespace and case to improve vector matching accuracy.

### 3. Data Commands
If you wish to regenerate or modify the knowledge base:
```bash
# Generate the 600k row large dataset
python dataset/generate_dataset.py

# Clean, deduplicate, and normalize the data
python dataset/clean_dataset.py
```

---

## 🔐 Credentials

### Application Login (Frontend)
| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `Admin` | `123456` |
| **User** | `Yash` | `123456` |

### Database Access (MySQL)
| Key | Value |
| :--- | :--- |
| **Host** | `localhost` |
| **Database** | `qa_system` |
| **Username** | `root` |
| **Password** | `admin123` |

---

## 🖥️ Alternative: Terminal/CLI Only
If you want to run the model directly in your terminal without the browser:
```bash
cd backend
python main.py
```

---

## 📁 Project Structure
```text
Question_Answearing_system/
├── backend/
│   ├── app.py                # Main FastAPI Server (Web Interface)
│   ├── main.py               # CLI Terminal Interface
│   ├── setup_mysql.py        # Database creation script
│   ├── migrate_users.py      # User credentials migration script
├── dataset/
│   ├── generate_dataset.py   # Synthesis engine (600k rows)
│   ├── clean_dataset.py      # Automated cleaning pipeline
│   ├── qa_dataset_clean.csv  # Final normalized dataset
├── frontend/                 # React (Vite) source code
├── model/                    # ML models, Vectorizer, and FAISS Index
└── requirements.txt          # Python dependencies
```

---

## 👨‍💻 Developed By
**Yash**
*Specialization: Information Technology | Semester VIII (Capstone Project)*
