from langgraph.graph import StateGraph, END
from agents.state import EssayState
from agents.research_agent import research_agent
from agents.brainstorm_agent import brainstorm_agent
from agents.outline_agent import outline_agent
from agents.draft_agent import draft_agent
from agents.critique_agent import critique_agent

def create_essay_workflow():
    """
    Create the complete 5-agent essay generation workflow.
    
    Flow: Research → Brainstorm → Outline → Draft → Critique → End
    """
    # Create the graph
    workflow = StateGraph(EssayState)
    
    # Add all 5 agents as nodes
    workflow.add_node("research", research_agent)
    workflow.add_node("brainstorm", brainstorm_agent)
    workflow.add_node("outline", outline_agent)
    workflow.add_node("draft", draft_agent)
    workflow.add_node("critique", critique_agent)
    
    # Define the flow (linear for now)
    workflow.add_edge("research", "brainstorm")
    workflow.add_edge("brainstorm", "outline")
    workflow.add_edge("outline", "draft")
    workflow.add_edge("draft", "critique")
    workflow.add_edge("critique", END)
    
    # Set the entry point
    workflow.set_entry_point("research")
    
    # Compile and return
    return workflow.compile()

def run_essay_generation(prompt: str, user_context: str = None) -> dict:
    """
    Convenience function to run the full workflow.
    
    Args:
        prompt: The college essay prompt
        user_context: Optional context about the student
    
    Returns:
        Final state with all agent outputs
    """
    # Create the workflow
    app = create_essay_workflow()
    
    # Initial state
    initial_state = {
        "prompt": prompt,
        "user_context": user_context,
        "research_analysis": "",
        "brainstorm_ideas": [],
        "selected_idea": "",
        "essay_outline": "",
        "essay_draft": "",
        "essay_critique": "",
        "current_agent": "research",
        "agent_times": {},
        "messages": []
    }
    
    # Run the workflow
    print("\n" + "="*70)
    print(" ESSAY MENTOR AI - MULTI-AGENT ESSAY GENERATION")
    print("="*70)
    print(f"\nPrompt: {prompt}\n")
    
    final_state = app.invoke(initial_state)
    
    # Print summary
    print("\n" + "="*70)
    print(" WORKFLOW COMPLETE - SUMMARY")
    print("="*70)
    
    total_time = sum(final_state['agent_times'].values())
    
    print(f"\n⏱️  Total Time: {total_time:.1f}s")
    print(f"\n📊 Agent Timings:")
    for agent, time_taken in final_state['agent_times'].items():
        print(f"   - {agent.capitalize()}: {time_taken:.1f}s")
    
    print(f"\n📝 Essay Word Count: {len(final_state['essay_draft'].split())} words")
    
    return final_state