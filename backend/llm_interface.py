import requests
import json

class OllamaInterface:
    """
    Interfaces with a locally running Ollama instance hosting the Llama 3 model.
    Runs entirely offline.
    """
    def __init__(self, model_name: str = "llama3.2:1b", host_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_url = f"{host_url}/api/generate"
        
    def check_connection(self):
        """
        Validates if the Ollama local API is listening.
        """
        try:
            response = requests.get("http://localhost:11434/")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def generate_response(self, prompt: str) -> str:
        """
        Sends an engineered prompt to local Llama 3 and streams the HTTP response back.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 1024,      # Minimal memory usage
                "num_predict": 80,     # Very short and fast responses
                "temperature": 0.2,    # Deterministic and faster
                "repeat_penalty": 1.3, # Strong penalty to avoid slow loops
                "top_k": 10,           # Minimal sampling candidates
                "top_p": 0.4
            }
        }
        
        try:
            # Set a 60-second timeout for the local API call
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "Error: No response generated.")
            
        except requests.exceptions.Timeout:
            return "Error: Ollama API timed out after 60 seconds. The model might be loading or the system is under high load."
        except requests.exceptions.RequestException as e:
            return f"Error communicating with local Ollama API: {e}"
