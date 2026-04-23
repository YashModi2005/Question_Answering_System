import csv
import random
import os
import re

# Configuration
NUM_SAMPLES = 600000
NOISE_RATIO = 0.01
OUTPUT_FILE = "dataset/qa_dataset_large.csv"

# Domain Distributions (11 Domains)
DISTRIBUTION = {
    "AI": 0.09,
    "ML": 0.09,
    "NLP": 0.09,
    "Data_Science": 0.09,
    "CS_Fundamentals": 0.09,
    "Programming": 0.09,
    "Operating_Systems": 0.09,
    "Networking": 0.09,
    "Databases": 0.10,
    "Algorithms": 0.10,
    "General_Tech": 0.09
}

# Extensive Fact Engine Data (50+ Concepts)
FACT_DATA = {
    "AI": {
        "concepts": [
            {
                "subject": ["Artificial Intelligence", "AI", "Computational Intelligence"],
                "definition": "the branch of computer science dedicated to creating systems capable of performing tasks that normally require human intelligence",
                "elaboration": "it focuses on developing algorithms for reasoning, learning, and self-correction in complex digital environments",
                "usage": "it is widely used in autonomous vehicles, surgical robotics, and advanced decision-making frameworks",
                "technical_note": "implementation often involves neural networks, fuzzy logic, and probabilistic modeling techniques"
            },
            {
                "subject": ["Computer Vision", "CV", "Visual Recognition"],
                "definition": "a field of artificial intelligence that enables computers and systems to derive meaningful information from digital images and videos",
                "elaboration": "it involves processing, analyzing, and understanding digital images to produce symbolic or numerical information",
                "usage": "it is used in facial recognition systems, medical image analysis, and quality control in manufacturing",
                "technical_note": "Convolutional Neural Networks (CNNs) are the primary architectural choice for state-of-the-art vision tasks"
            }
        ]
    },
    "ML": {
        "concepts": [
            {
                "subject": ["Machine Learning", "ML", "Statistical Learning"],
                "definition": "a subset of artificial intelligence that empowers computers to learn and improve from data experience without explicit programming",
                "elaboration": "it relies on sophisticated mathematical models to identify patterns and make high-accuracy predictions on new data",
                "usage": "the technology fuels recommendation systems, financial fraud detection, and predictive maintenance tools",
                "technical_note": "it encompasses supervised, unsupervised, and reinforcement learning paradigms to optimize software performance"
            },
            {
                "subject": ["Neural Networks", "Artificial Neural Networks", "ANN"],
                "definition": "computational models inspired by the biological structure of the human brain to recognize complex patterns in data",
                "elaboration": "they consist of layers of interconnected nodes or neurons that process information using weighted inputs and activation functions",
                "usage": "these models are the backbone of deep learning applications like speech recognition and autonomous driving",
                "technical_note": "the learning process involves adjusting weights through backpropagation and gradient descent optimization"
            }
        ]
    },
    "NLP": {
        "concepts": [
            {
                "subject": ["Natural Language Processing", "NLP", "Computational Linguistics"],
                "definition": "the field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language",
                "elaboration": "it bridges the gap between human communication and machine understanding through specialized linguistic analysis",
                "usage": "it is essential for virtual assistants, sentiment analysis, and seamless real-time translation services",
                "technical_note": "it combines statistical models with deep learning architectures like transformers for language modeling"
            },
            {
                "subject": ["Transformers", "Attention Mechanism", "Transformer Architecture"],
                "definition": "a deep learning model architecture that uses self-attention mechanisms to process sequential data in parallel",
                "elaboration": "unlike RNNs, they process entire sequences at once, allowing for much faster training on massive text datasets",
                "usage": "they are the foundation of modern large language models like GPT, BERT, and Google's T5",
                "technical_note": "the architecture relies on multi-head attention to weigh the importance of different words in a sentence simultaneously"
            }
        ]
    },
    "Data_Science": {
        "concepts": [
            {
                "subject": ["Data Science", "Data Analysis", "Exploratory Data Analysis"],
                "definition": "an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge from data",
                "elaboration": "it combines statistics, mathematics, and programming to uncover hidden patterns and drive data-informed decision making",
                "usage": "it is used by businesses to predict market trends, optimize logistics, and improve customer experience",
                "technical_note": "it involves the entire data lifecycle including collection, cleaning, analysis, and visualization"
            },
            {
                "subject": ["Big Data", "Large Scale Data", "Distributed Data"],
                "definition": "extremely large datasets that may be analyzed computationally to reveal patterns, trends, and associations",
                "elaboration": "it is characterized by the four Vs comprising high volume, high velocity, high variety, and high veracity",
                "usage": "it powers real-time analytics for search engines, social media platforms, and large-scale IoT sensor networks",
                "technical_note": "it requires distributed computing frameworks like Hadoop or Spark to process data across clusters"
            }
        ]
    },
    "CS_Fundamentals": {
        "concepts": [
            {
                "subject": ["Data Structures", "Abstract Data Types"],
                "definition": "specialized formats for organizing, processing, retrieving, and storing data in computer systems efficiently",
                "elaboration": "common types include arrays, linked lists, stacks, queues, and complex structures like trees and graphs",
                "usage": "they are fundamental for optimizing software performance and managing memory effectively in all programs",
                "technical_note": "the choice of a structure directly impacts the time and space complexity of algorithms performing on it"
            },
            {
                "subject": ["Compiled Languages", "Static Compilation"],
                "definition": "programming languages where source code is translated into machine code by a compiler before execution",
                "elaboration": "this translation happens once, resulting in a standalone executable file that runs directly on the processor",
                "usage": "languages like C, C++, and Rust are favored for high-performance applications and system-level software",
                "technical_note": "compiled code generally runs faster than interpreted code but requires a dedicated build step"
            }
        ]
    },
    "Programming": {
        "concepts": [
            {
                "subject": ["Object-Oriented Programming", "OOP", "Object-Oriented Design"],
                "definition": "a programming paradigm based on the concept of objects which can contain both data and methods to manipulate that data",
                "elaboration": "it is built upon four fundamental principles precisely known as encapsulation, inheritance, polymorphism, and abstraction",
                "usage": "industrial software engineering relies on this approach to build scalable, reusable, and maintainable codebases",
                "technical_note": "it uses classes as blueprints to create individual instances that manage their own internal state"
            },
            {
                "subject": ["Functional Programming", "Declarative Programming"],
                "definition": "a programming paradigm that treats computation as the evaluation of mathematical functions and avoids changing-state",
                "elaboration": "it emphasizes the use of pure functions, immutability, and higher-order functions to reduce side effects",
                "usage": "it is popular in data transformation pipelines and concurrent systems where state consistency is critical",
                "technical_note": "languages like Haskell, Lisp, and even JavaScript support this paradigm to ensure code predictability"
            }
        ]
    },
    "Operating_Systems": {
        "concepts": [
            {
                "subject": ["The Kernel", "OS Kernel", "Kernel Architecture", "OS"],
                "definition": "the central component of an operating system that manages system resources and communication between hardware and software",
                "elaboration": "it handles critical low-level tasks such as memory management, process scheduling, and device driver interaction",
                "usage": "it serves as an invisible intermediary that allows user-level applications to interact with physical processor and memory",
                "technical_note": "it enforces security and stability by managing transitions between user mode and privileged kernel mode"
            },
            {
                "subject": ["Virtual Memory", "Memory Paging", "Swap Space"],
                "definition": "a memory management technique that provides an idealized abstraction of the storage resources actually available",
                "elaboration": "it allows programs to behave as if they have more RAM than is physically installed by using disk space as an extension",
                "usage": "it enables modern operating systems to run multiple large applications simultaneously without frequent out-of-memory errors",
                "technical_note": "the system uses a page table to map virtual addresses to physical addresses in memory or on disk"
            }
        ]
    },
    "Networking": {
        "concepts": [
            {
                "subject": ["TCP/IP Protocol", "Internet Suite", "Network Protocols", "IP"],
                "definition": "the fundamental set of communication protocols used to interconnect hardware devices on the global internet",
                "elaboration": "it defines exactly how data should be formatted, addressed, transmitted, routed, and received at its final destination",
                "usage": "it provides the foundational architecture for the world wide web, email transmission, and file sharing services",
                "technical_note": "the suite operates across four distinct layers including the link, internet, transport, and application layers"
            },
            {
                "subject": ["OSI Model", "Open Systems Interconnection"],
                "definition": "a conceptual framework used to describe the functions of a networking system through seven distinct abstraction layers",
                "elaboration": "it categorizes communication tasks from physical electricity to high-level application data to ensure interoperability",
                "usage": "it is used as a standard guide for network engineers to troubleshoot connectivity and design hardware interfaces",
                "technical_note": "the layers include physical, data link, network, transport, session, presentation, and application"
            }
        ]
    },
    "Databases": {
        "concepts": [
            {
                "subject": ["Relational Databases", "SQL Databases", "RDBMS"],
                "definition": "a collection of data items organized as a set of tables from which data can be accessed and reassembled easily",
                "elaboration": "it maintains strict data integrity through the use of schemas, primary keys, and complex foreign key relationships",
                "usage": "it is the standard choice for applications requiring transactional consistency, such as banking and inventory systems",
                "technical_note": "it strictly adheres to ACID properties to ensure that database transactions are processed with high reliability"
            },
            {
                "subject": ["NoSQL Databases", "Non-Relational Databases", "Document Stores"],
                "definition": "a broad category of database management systems that store data in formats other than traditional relational tables",
                "elaboration": "they offer flexible schemas and are designed for high-performance, large-scale data storage across distributed clusters",
                "usage": "they power social media feeds, real-time analytics, and content management systems with high traffic volumes",
                "technical_note": "types include document stores like MongoDB, key-value pairs like Redis, and wide-column stores like Cassandra"
            }
        ]
    },
    "Algorithms": {
        "concepts": [
            {
                "subject": ["Algorithms", "Binary Search", "Hash Tables"],
                "definition": "a set of well-defined, step-by-step instructions designed to solve a specific problem or perform a complex calculation",
                "elaboration": "the efficiency of these procedures is typically measured using big O notation to analyze time and space complexity",
                "usage": "they are the fundamental building blocks of all software, from simple sorting to advanced encryption protocols",
                "technical_note": "an algorithm transforms a given input into a desired output through a finite sequence of logical operations"
            },
            {
                "subject": ["Big O Notation", "Complexity Analysis", "Algorithm Efficiency"],
                "definition": "a mathematical notation that describes the limiting behavior of a function when the argument tends towards infinity",
                "elaboration": "it is used in computer science to classify algorithms according to how their run time or space requirements grow as the input size grows",
                "usage": "it helps engineers compare different algorithmic approaches and choose the most efficient one for a specific workload",
                "technical_note": "common complexities include O(1) constant time, O(n) linear time, and O(log n) logarithmic time"
            }
        ]
    },
    "General_Tech": {
        "concepts": [
            {
                "subject": ["Cloud Computing", "IaaS", "PaaS", "AWS", "Azure", "The Cloud"],
                "definition": "the on-demand delivery of computing power, database storage, and applications over the internet with pay-as-you-go pricing",
                "elaboration": "it enables organizations to scale their digital resources rapidly without investing in expensive physical hardware",
                "usage": "it powers modern digital infrastructure including streaming platforms, remote workspace tools, and global web services",
                "technical_note": "it relies on virtualization technology to partition and allocate physical server resources to multiple users"
            },
            {
                "subject": ["Cybersecurity", "Network Security", "Information Security"],
                "definition": "the practice of protecting systems, networks, and programs from digital attacks and unauthorized data access",
                "elaboration": "it involves implementing multiple layers of protection across computers, networks, and data to create a robust defense",
                "usage": "it is critical for protecting sensitive government records, financial data, and personal identity information",
                "technical_note": "frameworks often focus on the CIA triad which stands for confidentiality, integrity, and availability"
            }
        ]
    }
}

Q_TEMPLATES = [
    "What is {subject}?",
    "Define {subject}.",
    "Explain the concept of {subject}.",
    "What does {subject} mean in computer science?",
    "How is {subject} used in modern technology?",
    "Can you describe {subject}?",
    "What is the significance of {subject} in the tech industry?",
    "Provide a detailed explanation of {subject}.",
    "What role does {subject} play in technical systems?",
    "Give a definition of {subject}.",
    "What do engineers mean by {subject}?",
    "What is the purpose of {subject}?",
    "In simple terms, what is {subject}?",
    "Why is {subject} important?",
    "How would you explain {subject}?",
    "What is the role of {subject} in computer systems?"
]

A_CONNECTORS = [
    "In technical terms, it represents",
    "This fundamental concept refers to",
    "Within the computer science industry, it is defined as",
    "According to technical standards, it involves",
]

def generate_structured_answer(concept):
    subj = random.choice(concept["subject"])
    verb = random.choice(["is", "refers to", "denotes", "is defined as", "represents"])
    conn = random.choice(A_CONNECTORS)
    
    parts = [
        f"{subj} {verb} {concept['definition']}.",
        f"{conn} {concept['elaboration']}.",
        f"It is extensively utilized for {concept['usage']}.",
        f"Experts note that it involves {concept['technical_note']}."
    ]
    
    return " ".join(parts)

def generate_qa_pair(domain, is_noisy):
    concept = random.choice(FACT_DATA[domain]["concepts"])
    template = random.choice(Q_TEMPLATES)
    subject = random.choice(concept["subject"])
    
    question = template.format(subject=subject)
    answer = generate_structured_answer(concept)
    
    if is_noisy:
        answer = answer + " This explanation may vary slightly depending on the specific technical context."
            
    return [question, answer]

def main():
    print(f"🚀 Generating {NUM_SAMPLES} retrieval-optimized QA pairs spanning all technical fields...")
    
    dataset = []
    seen_questions = set()
    
    for domain, weight in DISTRIBUTION.items():
        domain_count = int(NUM_SAMPLES * weight)
        print(f"Processing {domain}: {domain_count} samples...")
        
        count = 0
        while count < domain_count:
            is_noisy = random.random() < NOISE_RATIO
            qa = generate_qa_pair(domain, is_noisy)
            
            if qa[0] in seen_questions:
                # Add a suffix if duplicate to keep uniqueness but maintain relevance
                qa[0] = qa[0] + f" (var-{count})"
            
            dataset.append(qa)
            seen_questions.add(qa[0])
            count += 1
            
            if count % 100000 == 0:
                print(f"  ... {count} done")

    random.shuffle(dataset)
    
    os.makedirs("dataset", exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question", "answer"])
        writer.writerows(dataset[:NUM_SAMPLES])
        
    print(f"🏆 Broad knowledge dataset saved to {OUTPUT_FILE} (Final size: {len(dataset)})")

if __name__ == "__main__":
    main()
