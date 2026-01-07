from agents.research_agent import research_agent
from agents.brainstorm_agent import brainstorm_agent

# Initial state
state = {
    "prompt": "Reflect on a time when you questioned or challenged a belief or idea. What prompted your thinking? What was the outcome?",
    "user_context": None,
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

print("STEP 1: Research Agent")
state = {**state, **research_agent(state)}

print("\n\nSTEP 2: Brainstorm Agent")
state = {**state, **brainstorm_agent(state)}

print("\n" + "="*60)
print("BRAINSTORM IDEAS:")
print("="*60)
for i, idea in enumerate(state['brainstorm_ideas'], 1):
    print(f"\n--- IDEA {i} ---")
    print(idea[:300] + "...")

print("\n" + "="*60)
print("SELECTED IDEA:")
print("="*60)
print(state['selected_idea'])