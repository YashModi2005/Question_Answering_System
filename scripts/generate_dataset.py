import os
import csv
import wikipedia
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

# Force English Wikipedia
wikipedia.set_lang("en")

# Define target topics based on user request requirements
TOPICS = {
    "General Technology": [
        "Internet", "World Wide Web", "Computer network", "Cloud computing", "Wi-Fi",
        "Bluetooth", "Cybersecurity", "Computer hardware", "Computer software", "Operating system",
        "Server (computing)", "Database", "Smartphone", "Tablet computer", "Laptop",
        "Microprocessor", "Motherboard", "Computer memory", "Solid-state drive", "Hard disk drive",
        "Web browser", "Search engine", "Social media", "Email", "IP address"
    ],
    "Artificial Intelligence & Machine Learning": [
        "Artificial intelligence", "Machine learning", "Deep learning", "Neural network", "Natural language processing",
        "Computer vision", "Reinforcement learning", "Supervised learning", "Unsupervised learning", "Algorithm",
        "Data science", "Big data", "Chatbot", "Generative AI", "Large language model",
        "Transformer (machine learning architecture)", "Turing test", "Expert system", "Data mining", "Predictive analytics"
    ],
    "Programming Concepts": [
        "Computer programming", "Programming language", "Software engineering", "Source code", "Compiler",
        "Interpreter (computing)", "Algorithm", "Data structure", "Variable (computer science)", "Function (computer programming)",
        "Object-oriented programming", "Functional programming", "Debugging", "Version control", "Git",
        "Application programming interface", "Integrated development environment", "Syntax (programming languages)", "Recursion (computer science)", "Loop (computing)"
    ],
    "Specific Languages & Tech": [
        "Python (programming language)", "JavaScript", "Java (programming language)", "C++", "C (programming language)",
        "SQL", "HTML", "CSS", "TypeScript", "React (software)",
        "Node.js", "Docker (software)", "Linux", "Windows", "macOS"
    ],
    "Mathematics & Sciences": [
        "Mathematics", "Algebra", "Calculus", "Geometry", "Trigonometry",
        "Statistics", "Probability", "Physics", "Thermodynamics", "Quantum mechanics",
        "Gravity", "Electromagnetism", "Chemistry", "Biology", "Astronomy"
    ],
    "Vehicles & Transportation": [
        "Car", "Electric vehicle", "Hybrid vehicle", "Internal combustion engine", "Airplane",
        "Helicopter", "Train", "Bicycle", "Motorcycle", "Ship",
        "Submarine", "Spacecraft", "Public transport", "Traffic light", "Road"
    ],
    "Electronics & Engineering": [
        "Electronics", "Transistor", "Capacitor", "Resistor", "Inductor",
        "Integrated circuit", "Printed circuit board", "Microcontroller", "Sensor", "Actuator",
        "Battery (electricity)", "Electric motor", "Power supply", "Antenna (radio)", "Radar"
    ]
}

def clean_text(text: str) -> str:
    """Clean the text to be a strict 1-3 sentence definition without newlines."""
    # Split into sentences roughly
    sentences = [s.strip() + "." for s in text.split(". ")][:3]
    cleaned = " ".join(sentences).replace("\n", " ").replace("\r", " ").replace("..", ".")
    return cleaned.strip()

def process_topic(term: str) -> List[Tuple[str, str]]:
    """Fetch a wikipedia summary for a term and formulate multiple questions."""
    qa_pairs = []
    try:
        # Get the summary (limit to 3 sentences to keep it concise as requested)
        summary = wikipedia.summary(term, sentences=3, auto_suggest=False)
        answer = clean_text(summary)
        
        # Determine the primary subject name
        subject = term.split(" (")[0].lower() # e.g. "Python (programming language)" -> "python"
        
        # Formulate a set of standard questions
        qa_pairs.append((f"What is {subject}?", answer))
        qa_pairs.append((f"Define {subject}.", answer))
        qa_pairs.append((f"Explain what {subject} is.", answer))
        qa_pairs.append((f"What does {subject} mean?", answer))
        qa_pairs.append((f"Can you explain {subject}?", answer))
        qa_pairs.append((f"Tell me about {subject}.", answer))
        qa_pairs.append((f"Give me a definition of {subject}.", answer))
        
        print(f"Generated 7 variations for: {subject}")
        time.sleep(0.1) # Be nice to wikipedia API
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation error for {term}, picking first option: {e.options[0]}")
        try:
            summary = wikipedia.summary(e.options[0], sentences=3)
            answer = clean_text(summary)
            subject = term.split(" (")[0].lower()
            qa_pairs.append((f"What is {subject}?", answer))
            qa_pairs.append((f"Define {subject}.", answer))
            qa_pairs.append((f"Explain what {subject} is.", answer))
            qa_pairs.append((f"What does {subject} mean?", answer))
            qa_pairs.append((f"Can you explain {subject}?", answer))
        except Exception:
            pass
    except wikipedia.exceptions.PageError:
        print(f"Page not found for {term}")
    except Exception as e:
        print(f"Error processing {term}: {e}")
        
    return qa_pairs

def extend_dataset():
    target_csv = "dataset/qa_dataset_clean.csv"
    
    # Track existing questions to avoid duplicates
    existing_questions = set()
    if os.path.exists(target_csv):
        with open(target_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header if exists
            for row in reader:
                if len(row) >= 1:
                    existing_questions.add(row[0].lower().strip())
    
    # Flatten terms map
    all_terms = []
    for category, terms in TOPICS.items():
        all_terms.extend(terms)
        
    print(f"Preparing to process {len(all_terms)} core concepts...")
    
    new_pairs = []
    # Use thread pool to speed up API calls
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_topic, all_terms)
        for pairs in results:
            for q, a in pairs:
                # Deduplicate
                if q.lower().strip() not in existing_questions and len(a) > 20: 
                    new_pairs.append((q, a))
                    existing_questions.add(q.lower().strip())
                    
    print(f"\nGenerated {len(new_pairs)} unique, new high-quality QA pairs.")
    
    if len(new_pairs) > 0:
        # Determine if we need to write header (if file is completely empty or new)
        file_exists = os.path.exists(target_csv)
        file_empty = not file_exists or os.path.getsize(target_csv) == 0
        
        with open(target_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if file_empty:
                writer.writerow(["question", "answer"])
                
            for qa in new_pairs:
                writer.writerow(qa)
                
        print(f"Successfully appended to {target_csv}.")
    else:
        print("No new pairs needed to be appended (already exist or fetching failed).")

if __name__ == "__main__":
    extend_dataset()
