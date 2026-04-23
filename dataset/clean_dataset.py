import pandas as pd
import re
import os

INPUT_FILE = "dataset/qa_dataset_large.csv"
OUTPUT_FILE = "dataset/qa_dataset_clean.csv"

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print("Loading dataset for cleaning...")
    df = pd.read_csv(INPUT_FILE)
    
    initial_count = len(df)
    print(f"Initial row count: {initial_count}")

    # Remove duplicates
    df = df.drop_duplicates(subset=['question'])
    print(f"Rows after removing duplicate questions: {len(df)}")

    df = df.dropna()
    print(f"Rows after removing nulls: {len(df)}")

    # Basic cleaning
    df['question'] = df['question'].astype(str).str.strip()
    df['answer'] = df['answer'].astype(str).str.strip()
    
    # Remove nulls
    df = df.dropna()
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['question'])
    
    # Filter by minimum length (15 words for answer as per requirement)
    df = df[df['answer'].apply(lambda x: len(x.split()) >= 15)]
    
    # Filter by minimum question length
    df = df[df['question'].str.len() > 10]
    
    print(f"Final dataset size after strict cleaning: {len(df)}")
    
    # Save cleaned dataset
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Cleaned dataset saved successfully to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
