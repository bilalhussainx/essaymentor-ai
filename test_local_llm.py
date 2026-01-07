import requests
import json
import time

def chat_with_ollama(prompt, model="llama3.1:8b", temperature=0.7):
    """
    Simple function to chat with your local Ollama model
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 500,  # Max tokens to generate
            "top_p": 0.9,
        }
    }
    
    start_time = time.time()
    response = requests.post(url, json=payload)
    elapsed = time.time() - start_time
    
    result = response.json()
    
    print(f"⏱️  Generation time: {elapsed:.2f}s")
    print(f"📊 Tokens: ~{len(result['response'].split())}")
    print(f"🔥 Tokens/sec: ~{len(result['response'].split())/elapsed:.1f}")
    
    return result['response']

# Test 1: Basic generation
print("=" * 60)
print("TEST 1: Basic Essay Generation")
print("=" * 60)

prompt1 = """Write a compelling 150-word opening paragraph for a college essay about:
- Topic: Discovering a passion for AI through debugging code
- Tone: Authentic, specific, showing vulnerability
- Include one vivid detail"""

response1 = chat_with_ollama(prompt1)
print("\n📝 Generated text:")
print(response1)

# Test 2: Compare temperatures
print("\n" + "=" * 60)
print("TEST 2: Temperature Comparison")
print("=" * 60)

same_prompt = "Write one sentence about why college essays matter."

print("\n🌡️  Temperature 0.3 (focused):")
print(chat_with_ollama(same_prompt, temperature=0.3))

print("\n🌡️  Temperature 0.9 (creative):")
print(chat_with_ollama(same_prompt, temperature=0.9))

# Test 3: Essay critique
print("\n" + "=" * 60)
print("TEST 3: Essay Critique")
print("=" * 60)

sample_essay = """I've always loved coding. When I started programming,
I found it challenging but rewarding. Through hard work and dedication,
I became better at it. This experience taught me perseverance."""

critique_prompt = f"""As a college admissions expert, critique this essay:

{sample_essay}

Identify:
1. What's weak (be specific)
2. What's missing
3. One concrete improvement"""

critique = chat_with_ollama(critique_prompt, temperature=0.5)
print("\n💭 Critique:")
print(critique)