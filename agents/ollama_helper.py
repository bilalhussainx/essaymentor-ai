import requests
import time
from typing import Tuple

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

def call_ollama(
    prompt: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000,
    system_message: str = ""
) -> Tuple[str, float]:
    """
    Call Ollama API with error handling
    
    Returns:
        (response_text, time_taken_seconds)
    """
    # Combine system message and prompt
    if system_message:
        full_prompt = f"{system_message}\n\n{prompt}"
    else:
        full_prompt = prompt
    
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": max_tokens
        }
    }
    
    start = time.time()
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        elapsed = time.time() - start
        
        result = response.json()
        return result['response'], elapsed
    
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out (180s). Is the model loaded?")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Is it running? (ollama serve)")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")

def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with variables"""
    return template.format(**kwargs)