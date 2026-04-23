import pickle
import numpy as np

def test_inference(query):
    print(f"\n--- Testing Query: '{query}' ---")
    with open('model/qa_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
        
    print(f"Total Model Questions: {len(model_data['train_questions'])}")
    
    target_query = query.lower()
    
    import re
    target_query = re.sub(r'\b(a|an|the)\b\s+', '', target_query).strip()
    print(f"Normalized query for matching: '{target_query}'")
    
    train_questions_lower = np.char.lower(model_data['train_questions'].astype(str))
    
    # 1. Exact Match Try
    matches = np.where(train_questions_lower == target_query)[0]
    print(f"Exact matches without '?': {len(matches)}")
    
    # 2. Match with question mark
    if len(matches) == 0:
        matches = np.where(train_questions_lower == target_query + "?")[0]
        print(f"Exact matches with '?': {len(matches)}")
        
    if len(matches) > 0:
        match_idx = matches[0]
        print(f"SUCCESS: Found at index {match_idx}")
        print(f"Matched Question: {model_data['train_questions'][match_idx]}")
        print(f"Answer Preview: {model_data['train_answers'][match_idx][:100]}...")
    else:
        print("FAILED: No exact string match found in the numpy array.")
        
        # Fallback debug: See if the term even exists anywhere
        print("\nSearching for partial matches...")
        partial = np.char.find(train_questions_lower, target_query) != -1
        partial_matches = np.where(partial)[0]
        print(f"Questions containing '{target_query}': {len(partial_matches)}")
        for x in range(min(3, len(partial_matches))):
            idx = partial_matches[x]
            print(f"  - {model_data['train_questions'][idx]}")

if __name__ == '__main__':
    test_inference("What is a car?")
    test_inference("what is a computer?")
    test_inference("what is the internet?")
