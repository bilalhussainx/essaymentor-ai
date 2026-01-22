"""
Critique Agent - Enhanced with University Standards
Evaluates essay against university-specific criteria
"""

from agents.state import EssayState
from agents.ollama_helper import call_ollama
from pathlib import Path
import json

def load_university_profiles():
    profile_path = Path("data/university_profiles.json")
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

UNIVERSITY_PROFILES = load_university_profiles()

def critique_agent(state: EssayState) -> dict:
    """
    Critiques essay against university-specific standards
    Final quality check before returning to user
    """
    
    prompt = state['prompt']
    essay_draft = state['essay_draft']
    student_profile = state.get('student_profile', {})
    target_university = state.get('target_university', 'Generic')
    word_count_target = state.get('word_count', 650)
    
    # Get university standards
    univ_profile = UNIVERSITY_PROFILES.get(target_university, {})
    univ_prefs = univ_profile.get('essay_preferences', {})
    
    word_count_actual = len(essay_draft.split())
    
    critique_prompt = f"""Evaluate this college essay for {target_university} admission.

STUDENT: {student_profile.get('name', 'Student')}
TARGET UNIVERSITY: {target_university}
PROMPT: "{prompt}"

{target_university.upper()} STANDARDS:
Style: {univ_prefs.get('style', 'Authentic and specific')}

What {target_university} looks for:
{chr(10).join(f"- {w}" for w in univ_prefs.get('what_works', [])[:5])}

Red flags:
{chr(10).join(f"- {r}" for r in univ_prefs.get('red_flags', [])[:5])}

ESSAY TO EVALUATE:
{essay_draft}

WORD COUNT: {word_count_actual} words (target: {word_count_target})

PROVIDE DETAILED CRITIQUE:

## 1. OVERALL SCORE: [X/10]
Brief justification for score based on {target_university} standards

## 2. STRENGTHS
What works well in this essay:
- Specific details and authenticity
- Voice and writing quality
- Alignment with {target_university} values
- Unique/memorable elements
- Effective storytelling

## 3. WEAKNESSES
What needs improvement:
- Generic language or clichés
- Missed opportunities
- {target_university}-specific concerns
- Structure or flow issues
- Voice consistency problems

## 4. {target_university.upper()}-SPECIFIC ANALYSIS
- Does this align with {target_university}'s values? How?
- Would this stand out to {target_university} admissions officers?
- Any {target_university} red flags present?
- How well does it show fit for {target_university}?

## 5. SPECIFIC IMPROVEMENTS NEEDED
Line-by-line suggestions:
- Opening: [feedback]
- Body paragraphs: [feedback]
- Reflection: [feedback]
- Specific phrases to change: [list with improvements]

## 6. AUTHENTICITY CHECK
- Does this sound like a real 17-year-old {student_profile.get('name', 'student')}?
- Does the voice match student's profile (SAT {student_profile.get('sat_verbal', 790)}/800)?
- Any AI-sounding phrases?

## 7. FINAL RECOMMENDATION
- Ready to submit? Yes/No
- If no, what are the 2-3 most critical changes needed?
- If yes, any minor polishing suggestions?

Be honest and specific. This essay will be read by experienced {target_university} admissions officers."""

    print(f"[CRITIQUE AGENT] Evaluating essay against {target_university} standards...")
    
    critique = call_ollama(critique_prompt, temperature=0.4)
    
    print(f"[CRITIQUE AGENT] Critique complete.")
    
    # For now, final essay is the draft (later we'll implement revision loop)
    final_essay = essay_draft
    
    return {
        "critique": critique,
        "final_essay": final_essay,
        "current_agent": "complete"
    }