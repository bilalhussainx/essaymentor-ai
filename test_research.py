from agents.research_agent import research_agent
from agents.state import EssayState

# Test the research agent
test_state = {
    "prompt": "Discuss an accomplishment, event, or realization that sparked a period of personal growth and a new understanding of yourself or others.",
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

print("Testing Research Agent...")
result = research_agent(test_state)

print("\n" + "="*60)
print("RESEARCH ANALYSIS OUTPUT:")
print("="*60)
print(result['research_analysis'])