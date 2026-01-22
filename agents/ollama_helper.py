"""
LLM Helper - Claude Sonnet 4 Integration
Uses Anthropic Claude API for high-quality essay generation
Falls back to Ollama if Claude is not configured
"""

import os
import requests
import json

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1:8b"

# Claude Configuration - Uses Claude Sonnet 4 for 9.5/10 quality essays
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Claude Sonnet 4
USE_CLAUDE = bool(ANTHROPIC_API_KEY)  # Auto-detect: use Claude if API key is set

# Initialize Anthropic client if available
_anthropic_client = None

def _get_anthropic_client():
    """Lazy initialization of Anthropic client"""
    global _anthropic_client
    if _anthropic_client is None and USE_CLAUDE:
        try:
            import anthropic
            _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            print("[Claude] Sonnet 4 initialized for high-quality essay generation")
        except ImportError:
            print("[Warning] anthropic package not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            print(f"[Warning] Failed to initialize Claude: {e}")
            return None
    return _anthropic_client


def call_claude(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> str:
    """
    Call Claude API for high-quality responses

    Args:
        prompt: The prompt to send to Claude
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text response
    """
    client = _get_anthropic_client()
    if client is None:
        return "[Error: Claude client not available]"

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=temperature
        )
        return response.content[0].text

    except Exception as e:
        print(f"[Warning] Claude API error: {e}")
        return f"[Error: Claude API failed - {e}]"


def call_ollama(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    model: str = None
) -> str:
    """
    Call LLM API - automatically uses Claude if configured, otherwise Ollama

    Args:
        prompt: The prompt to send to the model
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        model: Model name (ignored if using Claude)

    Returns:
        Generated text response
    """

    # Use Claude if API key is configured (for high-quality essays)
    if USE_CLAUDE:
        return call_claude(prompt, temperature, max_tokens)

    # Fall back to Ollama for local/free generation
    model_name = model if model is not None else DEFAULT_MODEL

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        response.raise_for_status()

        result = response.json()
        return result.get("response", "")

    except requests.exceptions.Timeout:
        print(f"[Warning] Ollama request timed out after 300 seconds")
        return "[Error: Request timed out]"

    except requests.exceptions.ConnectionError:
        print(f"[Warning] Could not connect to Ollama at {OLLAMA_API_URL}")
        print(f"   Make sure Ollama is running: ollama serve")
        return "[Error: Could not connect to Ollama]"

    except requests.exceptions.RequestException as e:
        print(f"[Warning] Ollama request failed: {e}")
        return f"[Error: {e}]"

    except json.JSONDecodeError:
        print(f"[Warning] Invalid JSON response from Ollama")
        return "[Error: Invalid response format]"


def get_current_backend() -> str:
    """Returns which LLM backend is currently active"""
    if USE_CLAUDE:
        return f"Claude ({CLAUDE_MODEL})"
    return f"Ollama ({DEFAULT_MODEL})"


def list_available_models() -> list:
    """
    List all models available in Ollama

    Returns:
        List of model names
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        response.raise_for_status()

        result = response.json()
        models = [model['name'] for model in result.get('models', [])]
        return models

    except Exception as e:
        print(f"[Warning] Could not list Ollama models: {e}")
        return []


def check_model_exists(model_name: str) -> bool:
    """
    Check if a model exists in Ollama

    Args:
        model_name: Name of the model to check

    Returns:
        True if model exists, False otherwise
    """
    available_models = list_available_models()
    return model_name in available_models


def get_model_info(model_name: str) -> dict:
    """
    Get information about a specific model

    Args:
        model_name: Name of the model

    Returns:
        Dictionary with model information
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/show",
            json={"name": model_name},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"[Warning] Could not get info for {model_name}: {e}")
        return {}