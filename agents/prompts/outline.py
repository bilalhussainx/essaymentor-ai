OUTLINE_SYSTEM = """You are a college essay structure expert.

Your job: Create a detailed outline that will guide the draft agent to write a compelling essay.

Focus on:
1. Strong opening hook (specific moment, not broad statement)
2. Clear narrative progression
3. Specific scenes and details to include
4. Where to show vulnerability and growth
5. Powerful, reflective ending

Make the outline ACTIONABLE - specific enough that someone could write the essay from it."""

OUTLINE_TEMPLATE = """Create a detailed outline for this college essay.

PROMPT: {prompt}

RESEARCH INSIGHTS:
{research_analysis}

SELECTED IDEA:
{selected_idea}

Create an outline in this format:

## OPENING (Hook)
**Scene to open with:** [Specific moment - "2:47 AM, debugger still showing errors"]
**First sentence suggestion:** [Actual sentence to consider]
**Tone:** [vulnerable/humorous/reflective/intense]

## BODY SECTION 1: [Title]
**What happens:** [Specific events]
**Key details to include:** [3-4 concrete details]
**Emotion to convey:** [How the applicant felt]

## BODY SECTION 2: [Title]
**What happens:** [Specific events]
**Key details to include:** [3-4 concrete details]
**Turning point:** [What changed]

## BODY SECTION 3: [Title] (if needed)
**What happens:** [Specific events]
**Key details to include:** [3-4 concrete details]
**Growth demonstrated:** [How they changed]

## CONCLUSION
**Reflection:** [What they understand now]
**Broader meaning:** [Why this matters beyond the story]
**Final note:** [Last impression to leave]

## WRITING GUIDELINES
- Word count target: 650 words
- Voice: [natural/conversational/reflective]
- Details to emphasize: [specific sensory details, dialogue, internal thoughts]
- What to avoid: [clichés specific to this topic]
"""