"""
Outline Agent - Enhanced with RAG and University Preferences
Creates detailed paragraph-by-paragraph outline using:
- University-specific structure preferences
- Structural patterns from successful essay examples (RAG)
"""

from agents.state import EssayState
from agents.ollama_helper import call_ollama
from pathlib import Path
import json
from typing import List, Dict


def load_university_profiles():
    profile_path = Path("data/university_profiles.json")
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


UNIVERSITY_PROFILES = load_university_profiles()


def extract_essay_structures(retrieved_essays: List[Dict]) -> str:
    """
    Extract structural patterns from retrieved essays.

    Instead of showing full essays, this extracts the structure
    to help the outline agent learn from successful patterns.
    """
    if not retrieved_essays:
        return ""

    structures = "=== STRUCTURAL PATTERNS FROM SUCCESSFUL ESSAYS ===\n\n"

    for i, essay in enumerate(retrieved_essays[:3], 1):  # Top 3 examples
        text = essay.get('text', '')
        metadata = essay.get('metadata', {})

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        structures += f"Example {i} ({metadata.get('student', 'Unknown')} - {metadata.get('university', 'N/A')}):\n"

        for j, para in enumerate(paragraphs[:5], 1):  # First 5 paragraphs
            # Get first sentence and word count
            first_sentence = para.split('.')[0] + '.' if '.' in para else para[:100]
            word_count = len(para.split())
            structures += f"  Para {j} (~{word_count} words): {first_sentence[:80]}...\n"

        structures += f"  Overall structure: {len(paragraphs)} paragraphs, ~{len(text.split())} words\n\n"

    structures += "=== END STRUCTURAL PATTERNS ===\n\n"
    structures += "Notice how successful essays:\n"
    structures += "- Open with specific moments, not generic statements\n"
    structures += "- Build gradually toward insight\n"
    structures += "- End with reflection, not summary\n"

    return structures


def outline_agent(state: EssayState) -> dict:
    """
    Creates detailed essay outline following best approach from Brainstorm Agent.

    Enhanced with RAG:
    - Considers university-specific structure preferences
    - Learns structural patterns from successful essay examples
    """

    prompt = state['prompt']
    ideas = state['ideas']
    student_profile = state.get('student_profile', {})
    target_university = state.get('target_university', 'Generic')
    word_count = state.get('word_count', 650)

    # NEW: Get structural patterns from retrieved essays
    retrieved_essays = state.get('retrieved_essays', [])
    structure_examples = extract_essay_structures(retrieved_essays)
    
    # Get university preferences
    univ_profile = UNIVERSITY_PROFILES.get(target_university, {})
    univ_prefs = univ_profile.get('essay_preferences', {})
    
    outline_prompt = f"""Create a detailed paragraph-by-paragraph outline for {target_university}.

STUDENT: {student_profile.get('name', 'Student')}
VOICE: {student_profile.get('voice_characteristics', {}).get('overall_tone', 'Authentic')}

SELECTED APPROACH (from Brainstorm Agent):
{ideas}

TARGET UNIVERSITY: {target_university}
{target_university} PREFERS: {univ_prefs.get('style', 'Authentic and specific writing')}

TARGET LENGTH: {word_count} words
PROMPT: "{prompt}"

{structure_examples}

CREATE DETAILED OUTLINE:

## OPENING PARAGRAPH (Hook) - ~100 words
- Start with SPECIFIC MOMENT (exact time, place, sensory detail)
- NO generic opening ("Ever since I was young...", "I have always...")
- Drop reader into scene immediately
- What to include: [specific details]
- Tone: [appropriate for {target_university}]

## BODY PARAGRAPH 1 - ~150 words
- Purpose: [what this paragraph accomplishes]
- Scene/Content: [specific moment or explanation]
- Key details to include:
- Dialogue (if relevant):
- Showing not telling:
- Transition to next paragraph:

## BODY PARAGRAPH 2 - ~150 words
- Purpose:
- Scene/Content:
- Key details:
- Connection to previous paragraph:
- Building toward insight:

## BODY PARAGRAPH 3 - ~150 words
- Purpose:
- Scene/Content:
- Deepening the narrative:
- Setting up reflection:

## REFLECTION/CONCLUSION - ~100 words
- Insight EARNED through experience (not stated obviously)
- Connection to growth/future
- Alignment with {target_university}'s values
- Natural ending (no summarizing)
- Forward-looking but grounded

## STRUCTURAL NOTES:
- Overall narrative arc:
- Voice consistency throughout:
- {target_university}-specific elements to emphasize:
- Red flags to avoid:
- Specific details that must be included:

Provide DETAILED guidance for each section so Draft Agent can write confidently."""

    print(f"[OUTLINE AGENT] Creating detailed outline for {word_count}-word essay...")
    
    outline = call_ollama(outline_prompt, temperature=0.6)
    
    print(f"[OUTLINE AGENT] Outline complete. Ready for drafting.")
    
    return {
        "essay_outline": outline,
        "current_agent": "draft"
    }