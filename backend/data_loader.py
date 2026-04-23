import pandas as pd
import os

class DataLoader:
    """
    Handles loading the dataset using Pandas.
    Supports chunking to efficiently process large datasets like the 600K QA pairs.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Dataset not found at {self.filepath}")

    def load_data(self) -> pd.DataFrame:
        """
        Loads the entire dataset into a pandas DataFrame.
        """
        print(f"Loading dataset from {self.filepath}...")
        df = pd.read_csv(self.filepath)
        
        # Ensure 'question' and 'answer' columns exist
        if 'question' not in df.columns or 'answer' not in df.columns:
            raise ValueError("Dataset must contain 'question' and 'answer' columns.")
        
        # Drop rows with missing questions or answers
        df = df.dropna(subset=['question', 'answer'])
        
        # Ensure all questions and answers are strings
        df['question'] = df['question'].astype(str)
        df['answer'] = df['answer'].astype(str)
        
        print(f"Successfully loaded {len(df):,} valid records.")
        return df

    def get_batches(self, batch_size: int = 10000):
        """
        Generator that yields chunks of the dataset.
        Useful for generating embeddings without overloading RAM.
        """
        df = self.load_data()
        for i in range(0, len(df), batch_size):
            yield df.iloc[i : i + batch_size]
