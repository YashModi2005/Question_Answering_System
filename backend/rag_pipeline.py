from retriever import Retriever
from llm_interface import OllamaInterface

class RAGPipeline:
    """
    The orchestrator module that ties the Vector Database retrieval 
    together with the Generative AI (Ollama Llama 3).
    """
    def __init__(self, retriever: Retriever, llm: OllamaInterface):
        self.retriever = retriever
        self.llm = llm
        
    def generate_answer(self, user_question: str, session_id: str = None) -> tuple[str, list[dict], float]:
        """
        Retrieves the top contexts, engineers the prompt, 
        and extracts the generative text.
        Returns the (generative text, list of retrieved context metadata, time_taken)
        """
        import time
        start_total = time.time()
        
        # 1. Retrieve context with timing
        start_retrieve = time.time()
        contexts = self.retriever.retrieve_context(user_question, top_k=3, session_id=session_id)
        retrieval_time = time.time() - start_retrieve
        
        if not contexts:
            return "No relevant context found in the database. Please try a different query.", [], 0
            
        # 2. Extract and format context
        formatted_context = ""
        for idx, item in enumerate(contexts):
            doc = item['document']
            formatted_context += f"Result {idx+1}:\nQ: {doc['question']}\nA: {doc['answer']}\n\n"
            
        # 3. Prompt Engineering (Natural & Professional)
        prompt = f"""You are a Knowledge Assistant. Using the information below, provide a helpful and direct answer to the user's question.

RULES:
1. Answer strictly based on the provided context.
2. If the information is not there, say: "I'm sorry, I don't have specific details on that in my current knowledge base."
3. Do NOT mention "Results", "Chunks", or "Context" in your final answer. Just give the information naturally.
4. Be concise.

Information:
{formatted_context}

Question: {user_question}
Answer:"""

        # 4. Generate response with timing
        start_gen = time.time()
        response_text = self.llm.generate_response(prompt)
        gen_time = time.time() - start_gen
        
        total_time = time.time() - start_total
        
        print(f"\n--- Performance Log ---")
        print(f"Retrieval: {retrieval_time:.2f}s")
        print(f"LLM Gen:   {gen_time:.2f}s")
        print(f"Total:     {total_time:.2f}s")
        print(f"-----------------------\n")
        
        return response_text, contexts, total_time
