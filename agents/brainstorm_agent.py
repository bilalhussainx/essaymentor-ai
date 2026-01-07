from agents.state import EssayState
from agents.ollama_helper import call_ollama, format_prompt
from agents.prompts.brainstorm import BRAINSTORM_SYSTEM, BRAINSTORM_TEMPLATE
from langchain_core.messages import AIMessage
import time
import re

def brainstorm_agent(state: EssayState) -> dict:
    """
    Agent 2: Brainstorm Agent
    
    Generates 5 diverse essay ideas based on the prompt and research.
    
    Input: state['prompt'], state['research_analysis']
    Output: state['brainstorm_ideas'], state['selected_idea']
    """
    print("\n" + "="*60)
    print("💡 AGENT 2: BRAINSTORM AGENT")
    print("="*60)
    print("Generating creative essay ideas...")
    
    # Format the prompt
    prompt = format_prompt(
        BRAINSTORM_TEMPLATE,
        prompt=state['prompt'],
        research_analysis=state['research_analysis']
    )
    
    # Call Ollama with higher temperature for creativity
    start_time = time.time()
    ideas_text, generation_time = call_ollama(
        prompt=prompt,
        system_message=BRAINSTORM_SYSTEM,
        temperature=0.85,  # Higher temperature for creative brainstorming
        max_tokens=2000
    )
    total_time = time.time() - start_time
    
    # Extract individual ideas (simple parsing)
    ideas_list = re.findall(r'## IDEA \d+:.*?(?=## IDEA \d+:|## RECOMMENDATION|$)', ideas_text, re.DOTALL)
    
    # If parsing fails, just store the whole text
    if not ideas_list:
        ideas_list = [ideas_text]
    
    print(f"✅ Brainstorming complete ({generation_time:.1f}s)")
    print(f"   Generated {len(ideas_list)} ideas")
    
    # For now, select the first idea (later we can add selection logic)
    # Extract the recommendation if it exists
    recommendation = re.search(r'## RECOMMENDATION\s+\*\*Best Idea:\*\*\s+(.*?)(?:\n|$)', ideas_text, re.DOTALL)
    if recommendation:
        selected = recommendation.group(1).strip()
    else:
        selected = ideas_list[0] if ideas_list else ideas_text
    
    # Update state
    return {
        "brainstorm_ideas": ideas_list,
        "selected_idea": selected,
        "current_agent": "outline",
        "agent_times": {**state.get("agent_times", {}), "brainstorm": total_time},
        "messages": [AIMessage(content=f"Brainstorm Agent: Generated {len(ideas_list)} essay ideas")]
    }