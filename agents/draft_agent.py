"""
Draft Agent - Enhanced with Fine-Tuned Model Support
Can use either base Ollama model or fine-tuned HuggingFace model
"""

from agents.state import EssayState
from agents.ollama_helper import call_ollama
from pathlib import Path

# Model paths
BASE_MODEL = "llama3.1:8b"
FINETUNED_MODEL_PATH = "models/draft_agent_finetuned"

# Check if fine-tuned model exists
FINETUNED_AVAILABLE = Path(FINETUNED_MODEL_PATH).exists()

def load_finetuned_model():
    """Load fine-tuned model on first use (lazy loading)"""
    global _finetuned_model, _finetuned_tokenizer
    
    if '_finetuned_model' not in globals():
        print(f"[DRAFT AGENT] Loading fine-tuned model from {FINETUNED_MODEL_PATH}...")
        
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel
        
        # 4-bit config for 8GB VRAM
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.3",
            quantization_config=bnb_config,
            device_map="auto",
        )
        
        # Load LoRA adapters
        model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL_PATH)
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL_PATH)
        
        _finetuned_model = model
        _finetuned_tokenizer = tokenizer
        
        print("[DRAFT AGENT] Fine-tuned model loaded successfully!")
    
    return _finetuned_model, _finetuned_tokenizer

def generate_with_finetuned(prompt: str, temperature: float = 0.75, max_tokens: int = 1000) -> str:
    """Generate text using fine-tuned model"""
    
    model, tokenizer = load_finetuned_model()
    
    # Format prompt for Mistral
    formatted_prompt = f"""<s>[INST] You are an expert college essay writer who creates exceptional admissions essays.

{prompt} [/INST]

"""
    
    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    
    # Generate
    import torch
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            top_k=40,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the response (after [/INST])
    if "[/INST]" in generated_text:
        response = generated_text.split("[/INST]")[-1].strip()
    else:
        response = generated_text
    
    # Remove instruction echo - find where essay actually starts
    if '**' in response:
        # Essay starts at title
        response = response[response.index('**'):]
    elif '\n\n' in response:
        # Or after first double newline
        parts = response.split('\n\n', 1)
        if len(parts) > 1 and len(parts[0]) < 200:
            response = parts[1]
    
    return response
def draft_agent(state: EssayState, use_finetuned: bool = False) -> dict:  # ← Set to False
    """
    Writes complete essay following outline
    
    Args:
        state: Current essay state with all context
        use_finetuned: Use fine-tuned model if available (default: False - use base model)
    """
    
    prompt = state['prompt']
    outline = state['essay_outline']
    student_profile = state.get('student_profile', {})
    target_university = state.get('target_university', 'Generic')
    word_count = state.get('word_count', 650)
    previous_essays = state.get('other_essays_in_suite', [])
    
    # Build voice consistency context
    voice_context = ""
    if previous_essays:
        last_essay = previous_essays[-1]
        voice_context = f"\n\nPREVIOUS ESSAY VOICE (maintain exact consistency):\n{last_essay.get('text', '')[:300]}..."
    
    draft_prompt = f"""Write a complete college admissions essay for {target_university}.

STUDENT PROFILE:
Name: {student_profile.get('name', 'Student')}
Background: {student_profile.get('background', '')}
Voice: {student_profile.get('voice_characteristics', {}).get('overall_tone', 'Authentic')}
SAT Verbal: {student_profile.get('sat_verbal', 790)}/800 (99th percentile writer)

EXPERIENCES TO DRAW FROM:
{student_profile.get('major_experiences', [])[0] if student_profile.get('major_experiences') else 'N/A'}

ESSAY PROMPT: "{prompt}"

TARGET UNIVERSITY: {target_university}

DETAILED OUTLINE TO FOLLOW:
{outline}{voice_context}

YOUR TASK: Write the complete {word_count}-word essay

REQUIREMENTS:
1. **Follow outline structure exactly** - each paragraph as specified
2. **Use student's authentic voice** - match their vocabulary and tone
3. **Include specific, concrete details** - times, places, names, dialogue
4. **Show don't tell** - use scenes and moments, not statements
5. **Maintain voice consistency** - if this isn't first essay, match previous voice
6. **Align with {target_university}** - reflect their values and preferences
7. **99th percentile quality** - sophisticated but natural vocabulary, varied sentences
8. **Natural reflection** - insight earned through experience, not obvious lessons

TARGET LENGTH: {word_count} words (important: stay close to this)

Write ONLY the essay text. No preamble, no title, no commentary. Just the essay."""

    print(f"[DRAFT AGENT] Writing {word_count}-word essay for {target_university}...")
    print(f"[DRAFT AGENT] Using base model: {BASE_MODEL}")
    
    # Always use base model (proven to perform best)
    essay = call_ollama(draft_prompt, temperature=0.75, model=BASE_MODEL)
    
    word_count_actual = len(essay.split())
    print(f"[DRAFT AGENT] Draft complete. {word_count_actual} words written.")
    
    return {
        "essay_draft": essay,
        "current_agent": "critique"
    }