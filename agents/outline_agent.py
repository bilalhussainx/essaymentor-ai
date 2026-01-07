from agents.state import EssayState
from agents.ollama_helper import call_ollama, format_prompt
from agents.prompts.outline import OUTLINE_SYSTEM, OUTLINE_TEMPLATE
from langchain_core.messages import AIMessage
import time

def outline_agent(state: EssayState) -> dict:
    """
    Agent 3: Outline Agent
    
    Creates a detailed structural outline for the essay.
    
    Input: state['prompt'], state['research_analysis'], state['selected_idea']
    Output: state['essay_outline']
    """
    print("\n" + "="*60)
    print("📋 AGENT 3: OUTLINE AGENT")
    print("="*60)
    print("Creating essay structure...")
    
    # Format the prompt
    prompt = format_prompt(
        OUTLINE_TEMPLATE,
        prompt=state['prompt'],
        research_analysis=state['research_analysis'],
        selected_idea=state['selected_idea']
    )
    
    # Call Ollama
    start_time = time.time()
    outline, generation_time = call_ollama(
        prompt=prompt,
        system_message=OUTLINE_SYSTEM,
        temperature=0.6,  # Moderate temperature for structured creativity
        max_tokens=1500
    )
    total_time = time.time() - start_time
    
    print(f"✅ Outline complete ({generation_time:.1f}s)")
    print(f"   Outline length: {len(outline.split())} words")
    
    # Update state
    return {
        "essay_outline": outline,
        "current_agent": "draft",
        "agent_times": {**state.get("agent_times", {}), "outline": total_time},
        "messages": [AIMessage(content="Outline Agent: Created detailed essay structure")]
    }