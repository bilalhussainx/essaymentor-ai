"""
Brainstorm Agent - Enhanced with RAG (Retrieval-Augmented Generation)
Generates essay ideas using Profile Agent's selected experiences AND
successful essay examples retrieved from the vector database.
"""

from agents.state import EssayState
from agents.ollama_helper import call_ollama

def brainstorm_agent(state: EssayState) -> dict:
    """
    Generates essay approaches using selected experiences.

    Now enhanced with RAG:
    - Uses Profile Agent's experience recommendations
    - References successful essay examples from vector database
    - Learns from proven narrative structures and techniques
    """

    prompt = state['prompt']
    profile_analysis = state['profile_analysis']
    prompt_analysis = state['prompt_analysis']
    student_profile = state.get('student_profile', {})
    target_university = state.get('target_university', 'Generic')
    previous_essays = state.get('other_essays_in_suite', [])

    # NEW: Get RAG context (retrieved successful essays)
    rag_context = state.get('rag_context', '')

    # Build voice consistency context
    voice_context = ""
    if previous_essays:
        voice_context = f"\n\nPREVIOUS ESSAY VOICE (maintain consistency):\n{previous_essays[-1].get('text', '')[:200]}..."

    # Build RAG examples section
    rag_section = ""
    if rag_context:
        rag_section = f"""

{rag_context}

LEARNING FROM EXAMPLES:
Based on the successful essays above, notice:
- How they open with specific, vivid moments (not generic statements)
- How they weave personal experience with broader themes
- Their authentic voice and natural storytelling
- How they show growth through concrete examples

Apply these techniques to the approaches below, but create ORIGINAL content.
"""

    brainstorm_prompt = f"""Generate essay approaches for {target_university} based on strategic profile analysis and successful essay examples.

STUDENT CONTEXT:
Name: {student_profile.get('name', 'Student')}
Background: {student_profile.get('background', '')}
Voice: {student_profile.get('voice_characteristics', {}).get('overall_tone', 'Authentic')}
SAT Verbal: {student_profile.get('sat_verbal', 790)}/800

SELECTED EXPERIENCES & STRATEGY (from Profile Agent):
{profile_analysis}

PROMPT ANALYSIS (from Research Agent):
{prompt_analysis}

TARGET UNIVERSITY: {target_university}
PROMPT: "{prompt}"{voice_context}
{rag_section}
YOUR TASK: Generate 3-4 distinct essay approaches

For EACH approach, provide:

**APPROACH [Number]: [Brief Title]**

1. **Central Experience:** Which experience(s) to center the essay on
2. **Opening Hook:** Specific moment to start (time, place, sensory detail)
3. **Key Scenes:** 2-3 specific scenes/moments to include
4. **Narrative Arc:** How the story progresses
5. **Reflection/Insight:** What growth or realization to explore
6. **University Fit:** Why this approach works for {target_university}
7. **Distinctive Angle:** What makes this unique/memorable

CRITICAL REQUIREMENTS:
- Use experiences Profile Agent identified as most compelling
- Align with {target_university}'s values and preferences
- Avoid clichés and red flags for {target_university}
- Each approach should be distinctly different from the others
- Include specific details (names, times, places)
- Show don't tell through concrete scenes

After presenting all approaches, RECOMMEND the best one and explain why it's strongest for this student applying to {target_university}."""

    print(f"[BRAINSTORM AGENT] Generating essay approaches for {target_university}...")
    
    ideas = call_ollama(brainstorm_prompt, temperature=0.8)
    
    print(f"[BRAINSTORM AGENT] Generated multiple approaches. Recommended best fit.")
    
    return {
        "ideas": ideas,
        "essay_approach": "Generated university-specific approaches",
        "current_agent": "outline"
    }