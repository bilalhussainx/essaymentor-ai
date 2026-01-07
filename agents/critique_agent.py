from agents.state import EssayState
from agents.ollama_helper import call_ollama, format_prompt
from agents.prompts.critique import CRITIQUE_SYSTEM, CRITIQUE_TEMPLATE
from langchain_core.messages import AIMessage
import time

def critique_agent(state: EssayState) -> dict:
    """
    Agent 5: Critique Agent
    
    Provides expert evaluation and feedback on the essay.
    NOTE: In production (Week 6), this will use Claude API for highest quality.
    
    Input: state['prompt'], state['essay_draft']
    Output: state['essay_critique']
    """
    print("\n" + "="*60)
    print("🔍 AGENT 5: CRITIQUE AGENT")
    print("="*60)
    print("Analyzing essay quality...")
    
    # Format the prompt
    prompt = format_prompt(
        CRITIQUE_TEMPLATE,
        prompt=state['prompt'],
        essay=state['essay_draft']
    )
    
    # Call Ollama with lower temperature for analytical task
    start_time = time.time()
    critique, generation_time = call_ollama(
        prompt=prompt,
        system_message=CRITIQUE_SYSTEM,
        temperature=0.4,  # Low temperature for consistent analysis
        max_tokens=2000
    )
    total_time = time.time() - start_time
    
    print(f"✅ Critique complete ({generation_time:.1f}s)")
    
    # Update state
    return {
        "essay_critique": critique,
        "current_agent": "complete",
        "agent_times": {**state.get("agent_times", {}), "critique": total_time},
        "messages": [AIMessage(content="Critique Agent: Provided detailed feedback")]
    }