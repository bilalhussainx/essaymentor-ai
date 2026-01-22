"""
Profile Agent (Agent 0)
Analyzes student background and selects most compelling experiences 
for specific essay prompt and target university
"""

from typing import Dict
from agents.state import EssayState
from agents.ollama_helper import call_ollama
import json
from pathlib import Path

def load_university_profiles() -> Dict:
    """Load university profiles from JSON"""
    profile_path = Path("data/university_profiles.json")
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

UNIVERSITY_PROFILES = load_university_profiles()

def profile_agent(state: EssayState) -> dict:
    """
    Analyzes student profile and selects best experiences for this prompt and university
    
    This agent runs FIRST and determines:
    1. Which of the student's experiences to feature
    2. How to align with target university's values
    3. What angle would be most compelling
    4. Specific details to include
    """
    
    prompt = state['prompt']
    student_profile = state.get('student_profile', {})
    target_university = state.get('target_university', 'Generic')
    essay_type = state.get('essay_type', 'common_app')
    previous_essays = state.get('other_essays_in_suite', [])
    
    # Get university profile
    univ_profile = UNIVERSITY_PROFILES.get(target_university, {})
    univ_values = univ_profile.get('values', [])
    univ_preferences = univ_profile.get('essay_preferences', {})
    
    # Track what's been used in other essays
    used_experiences = []
    if previous_essays:
        for essay in previous_essays:
            used_exp = essay.get('main_experience', '')
            if used_exp:
                used_experiences.append(used_exp)
    
    # Build profile analysis prompt
    profile_prompt = f"""You are an expert college admissions consultant analyzing a student's profile to select the most compelling experiences for their {target_university} application essay.

STUDENT PROFILE:
Name: {student_profile.get('name', 'Student')}
Background: {student_profile.get('background', '')}
Location: {student_profile.get('location', '')}
SAT Verbal: {student_profile.get('sat_verbal', 'N/A')}/800

KEY EXPERIENCES:
{json.dumps(student_profile.get('major_experiences', []), indent=2)}

ACTIVITIES:
{', '.join(student_profile.get('activities', []))}

INTERESTS:
{json.dumps(student_profile.get('interests', {}), indent=2)}

TARGET UNIVERSITY: {target_university}

{target_university.upper()} VALUES:
{chr(10).join(f"- {v}" for v in univ_values)}

{target_university.upper()} ESSAY PREFERENCES:
Style: {univ_preferences.get('style', 'Authentic and specific')}

What works at {target_university}:
{chr(10).join(f"- {w}" for w in univ_preferences.get('what_works', [])[:5])}

Red flags to avoid:
{chr(10).join(f"- {r}" for r in univ_preferences.get('red_flags', [])[:5])}

ESSAY PROMPT: {prompt}
ESSAY TYPE: {essay_type}

EXPERIENCES ALREADY USED IN OTHER ESSAYS (avoid repeating):
{', '.join(used_experiences) if used_experiences else 'None - this is first essay'}

YOUR TASK - Provide detailed strategic analysis:

## 1. BEST EXPERIENCES TO FEATURE (2-3 specific experiences)
For each experience, explain:
- Which specific experience from their profile
- Why it's compelling for THIS university specifically
- How it connects to the prompt
- What makes it unique/distinctive

## 2. RECOMMENDED ESSAY ANGLE
- Most authentic way to answer this prompt
- Theme that resonates with {target_university}
- How to showcase student's unique perspective
- Connection between experience and growth/insight

## 3. UNIVERSITY FIT ANALYSIS
- Which aspects of student align with {target_university}'s values
- What this student would contribute to campus
- Why this student is a good match for {target_university}

## 4. SPECIFIC DETAILS TO INCLUDE
List concrete details that would make essay vivid:
- Names of people, places, organizations
- Specific times, dates, locations
- Numbers, statistics, measurements
- Quotes or dialogue
- Sensory details
- Technical specifics (if relevant)

## 5. WHAT TO AVOID
- Which experiences would be cliché for this prompt
- What would misalign with {target_university}'s values
- Generic approaches to avoid
- {target_university}'s specific red flags to watch out for

Be strategic and specific. This analysis will guide all subsequent agents."""

    print(f"[PROFILE AGENT] Analyzing {student_profile.get('name', 'student')}'s profile for {target_university}...")
    
    # Call model
    analysis = call_ollama(profile_prompt, temperature=0.6)
    
    print(f"[PROFILE AGENT] Analysis complete. Selected experiences for {essay_type}.")
    
    return {
        "profile_analysis": analysis,
        "selected_experiences": analysis,  # Used by downstream agents
        "university_alignment": f"Analyzed for {target_university} fit",
        "current_agent": "research"
    }