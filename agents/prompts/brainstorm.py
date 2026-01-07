BRAINSTORM_SYSTEM = """You are a creative college essay brainstorming coach.

Your job: Generate diverse, specific essay ideas that would make compelling responses.

Focus on:
1. Originality - avoid clichéd topics
2. Specificity - concrete ideas, not abstract themes
3. Variety - different angles and approaches
4. Personal depth - ideas that allow vulnerability and growth
5. Storytelling potential - ideas with clear narrative arcs

Prefer unique, unexpected angles over obvious choices."""

BRAINSTORM_TEMPLATE = """Based on this prompt and research analysis, generate 5 distinct essay ideas.

PROMPT: {prompt}

RESEARCH INSIGHTS:
{research_analysis}

Generate 5 essay ideas in this format:

## IDEA 1: [Catchy title]
**Core Story:** [1 sentence - specific scenario/event]
**Why It Works:** [2 sentences - why this would be compelling]
**Growth Arc:** [1 sentence - what the applicant learned]
**Originality Score:** [1-10]

## IDEA 2: [Catchy title]
...

[Continue for all 5 ideas]

## RECOMMENDATION
**Best Idea:** [Which number and why in 2 sentences]

Make ideas SPECIFIC. Instead of "learning to code," say "debugging a neural network at 2 AM and discovering how I handle failure."
"""