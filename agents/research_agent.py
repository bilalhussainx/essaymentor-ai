from agents.state import EssayState
from agents.ollama_helper import call_ollama, format_prompt
from agents.prompts.research import RESEARCH_SYSTEM, RESEARCH_TEMPLATE
from langchain_core.messages import AIMessage
import time

def research_agent(state: EssayState) -> dict:
    """
    Agent 1: Research Agent
    
    Analyzes the essay prompt to understand what it's really asking for.
    This helps subsequent agents write more targeted essays.
    
    Input: state['prompt']
    Output: state['research_analysis']
    """
    print("\n" + "="*60)
    print("🔍 AGENT 1: RESEARCH AGENT")
    print("="*60)
    print(f"Analyzing prompt: {state['prompt'][:80]}...")
    
    # Format the prompt
    prompt = format_prompt(RESEARCH_TEMPLATE, prompt=state['prompt'])
    
    # Call Ollama
    start_time = time.time()
    analysis, generation_time = call_ollama(
        prompt=prompt,
        system_message=RESEARCH_SYSTEM,
        temperature=0.5,  # Lower temperature for analytical task
        max_tokens=1500
    )
    total_time = time.time() - start_time
    
    print(f"✅ Research complete ({generation_time:.1f}s)")
    print(f"   Analysis length: {len(analysis.split())} words")
    
    # Update state
    return {
        "research_analysis": analysis,
        "current_agent": "brainstorm",
        "agent_times": {**state.get("agent_times", {}), "research": total_time},
        "messages": [AIMessage(content=f"Research Agent: Analyzed prompt, found key insights")]
    }