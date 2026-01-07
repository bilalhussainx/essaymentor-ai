from agents.state import EssayState
from agents.ollama_helper import call_ollama, format_prompt
from agents.prompts.draft import DRAFT_SYSTEM, DRAFT_TEMPLATE
from langchain_core.messages import AIMessage
import time

def draft_agent(state: EssayState) -> dict:
    """
    Agent 4: Draft Agent (THE KEY AGENT)
    
    Writes the actual essay following the outline.
    This is where the fine-tuned model will be used in Week 4.
    
    Input: state['prompt'], state['research_analysis'], state['essay_outline']
    Output: state['essay_draft']
    """
    print("\n" + "="*60)
    print("✍️  AGENT 4: DRAFT AGENT")
    print("="*60)
    print("Writing the essay...")
    
    # Format the prompt
    prompt = format_prompt(
        DRAFT_TEMPLATE,
        prompt=state['prompt'],
        outline=state['essay_outline'],
        research_analysis=state['research_analysis']
    )
    
    # Call Ollama
    # NOTE: In Week 4, this will use your fine-tuned model
    start_time = time.time()
    essay, generation_time = call_ollama(
        prompt=prompt,
        system_message=DRAFT_SYSTEM,
        temperature=0.75,  # Balanced creativity and coherence
        max_tokens=2500    # Enough for 650+ words
    )
    total_time = time.time() - start_time
    
    word_count = len(essay.split())
    
    print(f"✅ Draft complete ({generation_time:.1f}s)")
    print(f"   Word count: {word_count} words")
    
    # Update state
    return {
        "essay_draft": essay,
        "current_agent": "critique",
        "agent_times": {**state.get("agent_times", {}), "draft": total_time},
        "messages": [AIMessage(content=f"Draft Agent: Wrote {word_count}-word essay")]
    }