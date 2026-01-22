"""
Research Agent - Enhanced with University Context
Analyzes essay prompt considering target university's preferences
"""

from agents.state import EssayState
from agents.ollama_helper import call_ollama
import json
from pathlib import Path

def load_university_profiles():
    """Load university profiles"""
    profile_path = Path("data/university_profiles.json")
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

UNIVERSITY_PROFILES = load_university_profiles()

def research_agent(state: EssayState) -> dict:
    """
    Analyzes essay prompt with university-specific context
    Now considers what the university wants to learn about the student
    """
    
    prompt = state['prompt']
    profile_analysis = state.get('profile_analysis', '')
    target_university = state.get('target_university', 'Generic')
    essay_type = state.get('essay_type', 'common_app')
    
    # Get university preferences
    univ_profile = UNIVERSITY_PROFILES.get(target_university, {})
    univ_prefs = univ_profile.get('essay_preferences', {})
    
    research_prompt = f"""Analyze this college essay prompt for a student applying to {target_university}.

ESSAY PROMPT: "{prompt}"

{target_university.upper()} CONTEXT:
Essay Style: {univ_prefs.get('style', 'Authentic and specific')}

What {target_university} looks for:
{chr(10).join(f"- {w}" for w in univ_prefs.get('what_works', [])[:4])}

Red flags at {target_university}:
{chr(10).join(f"- {r}" for r in univ_prefs.get('red_flags', [])[:4])}

STUDENT'S SELECTED EXPERIENCES (from Profile Agent):
{profile_analysis[:600]}...

ANALYSIS NEEDED:

1. **WHAT IS THIS PROMPT REALLY ASKING?**
   - Beyond surface level, what does this question want to reveal?
   - What aspect of the student are they trying to understand?

2. **WHAT DOES {target_university} WANT TO LEARN?**
   - Why does {target_university} ask THIS specific question?
   - What are they looking for in the answer?
   - How does this connect to {target_university}'s values?

3. **COMMON PITFALLS**
   - What mistakes do students typically make with this prompt?
   - Generic approaches to avoid
   - Clichés specific to this prompt
   - {target_university}-specific mistakes to avoid

4. **HOW TO STAND OUT AT {target_university}**
   - What would make an essay memorable to {target_university} admissions?
   - What angle would align with {target_university}'s preferences?
   - How to be authentic while showing {target_university} fit?

5. **TONE AND STYLE FOR {target_university}**
   - What writing style resonates with {target_university}?
   - Balance of formal vs. conversational
   - Level of technical detail appropriate
   - How to show personality while being substantive

Provide specific, actionable analysis that will guide essay development."""

    print(f"[RESEARCH AGENT] Analyzing prompt for {target_university}...")
    
    analysis = call_ollama(research_prompt, temperature=0.5)
    
    print(f"[RESEARCH AGENT] Analysis complete. Identified key themes and {target_university} preferences.")
    
    return {
        "prompt_analysis": analysis,
        "prompt_type": f"analyzed for {target_university}",
        "current_agent": "brainstorm"
    }