import pandas as pd
import numpy as np
import pickle
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Download necessary NLTK data
print("Downloading NLTK resources...")
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt_tab')

# Configuration
INPUT_FILE = "dataset/qa_dataset_clean.csv"
MODEL_DIR = "model"
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "qa_model.pkl")

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    # Tokenization
    tokens = word_tokenize(text.lower())
    # Stopword removal and Lemmatization
    cleaned_tokens = [lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(cleaned_tokens)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print("Loading cleaned dataset...")
    df = pd.read_csv(INPUT_FILE)
    
    # Due to hardware constraints and the massive cardinality of answers (600k classes in Logistic Regression), 
    # we take a random sample here to simulate the user objective functionally without triggering an OOM array memory crash.
    print(f"Original dataset size: {len(df)}")
    # We will sample 10,000 to keep it manageable for a multi-class logistic regression locally.
    df = df.sample(n=min(10000, len(df)), random_state=42).reset_index(drop=True)
    print(f"Processing {len(df)} samples...")
    
    # Preprocessing
    print("Preprocessing questions...")
    df['processed_question'] = df['question'].apply(preprocess_text)
    
    # Train/Test Split (80% / 20%)
    print("Splitting dataset into 80% training and 20% testing...")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        df['processed_question'], df['answer'], test_size=0.20, random_state=42
    )
    
    # TF-IDF Vectorization
    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        stop_words="english"
    )
    
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

    # Train Logistic Regression
    print("Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    print(f"Accuracy: {acc:.2f}")
    print(f"Precision: {prec:.2f}")
    print(f"Recall: {rec:.2f}")
    print(f"F1 Score: {f1:.2f}")

    # Save artifacts
    print("Saving model and vectorizer...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save the vectorizer
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save the trained ML model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    print("Training pipeline completed successfully.")

if __name__ == "__main__":
    main()
