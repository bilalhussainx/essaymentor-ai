"""
RAG Retrieval Agent - Finds similar successful essays

EDUCATIONAL NOTE:
- This agent sits between Profile and Brainstorm agents
- It searches the vector database for relevant examples
- Returns 3-5 similar essays to inform other agents
- This is the "Retrieval" part of RAG (Retrieval-Augmented Generation)
"""

from typing import Dict, List
from agents.state import EssayState

# Import will be done lazily to avoid circular imports
_db_manager = None


def get_db_manager():
    """Lazy initialization of ChromaDB manager."""
    global _db_manager
    if _db_manager is None:
        from vector_db.chromadb_manager import ChromaDBManager
        _db_manager = ChromaDBManager()
    return _db_manager


def create_search_query(state: EssayState) -> str:
    """
    Build an effective search query from the essay state.

    Args:
        state: Current pipeline state with prompt, profile, etc.

    Returns:
        Optimized search query string

    How it works:
        - Combines user's essay prompt
        - Adds key themes from profile analysis
        - Adds target university context
        - Creates rich query for better retrieval
    """
    query_parts = []

    # Add the essay prompt
    prompt = state.get('prompt', '')
    if prompt:
        query_parts.append(prompt)

    # Add profile analysis themes if available
    profile_analysis = state.get('profile_analysis', '')
    if profile_analysis:
        # Extract key phrases from profile analysis (first 200 chars)
        query_parts.append(profile_analysis[:200])

    # Add student profile info
    student_profile = state.get('student_profile', {})
    if student_profile:
        # Add background
        background = student_profile.get('background', '')
        if background:
            query_parts.append(background)

        # Add interests
        interests = student_profile.get('interests', {})
        if isinstance(interests, dict):
            interest_values = list(interests.values())[:2]
            query_parts.extend(str(v) for v in interest_values)

    # Add target university
    target_university = state.get('target_university', '')
    if target_university:
        query_parts.append(f"essay for {target_university}")

    # Combine into single query
    search_query = " ".join(str(p) for p in query_parts if p)

    return search_query


def explain_retrieval(result: Dict, state: EssayState) -> str:
    """
    Explain why this essay was retrieved.

    Helps other agents understand the relevance.
    """
    reasons = []

    # Check topic match
    essay_topic = result['metadata'].get('topic', '')
    prompt = state.get('prompt', '').lower()

    if essay_topic and essay_topic.lower() in prompt:
        reasons.append(f"matches topic '{essay_topic}'")

    # Check university match
    essay_univ = result['metadata'].get('university', '')
    target_univ = state.get('target_university', '')
    if essay_univ and target_univ and essay_univ.lower() == target_univ.lower():
        reasons.append(f"same target university ({essay_univ})")

    # Check themes
    essay_themes = result['metadata'].get('themes', '')
    if essay_themes:
        reasons.append(f"themes: {essay_themes[:50]}")

    # Check score
    score = result['metadata'].get('score', 0)
    if score:
        reasons.append(f"high quality (score: {score}/10)")

    return "; ".join(reasons) if reasons else "semantic similarity"


def format_retrieved_essays(retrieved_essays: List[Dict], state: EssayState) -> str:
    """
    Format retrieved essays for consumption by other agents.

    Returns:
        Formatted string to include in agent prompts

    This is used by Brainstorm/Outline agents to learn from examples.
    """
    if not retrieved_essays:
        return "No similar examples found in database."

    formatted = "=== SUCCESSFUL ESSAY EXAMPLES (for reference) ===\n\n"

    for i, essay in enumerate(retrieved_essays, 1):
        metadata = essay.get('metadata', {})

        formatted += f"EXAMPLE {i}:\n"
        formatted += f"Student: {metadata.get('student', 'N/A')}\n"
        formatted += f"Target University: {metadata.get('university', 'N/A')}\n"
        formatted += f"Essay Type: {metadata.get('essay_type', 'N/A')}\n"
        formatted += f"Quality Score: {metadata.get('score', 'N/A')}/10\n"
        formatted += f"Topic: {metadata.get('topic', 'N/A')}\n"
        formatted += f"Why relevant: {essay.get('why_retrieved', 'Similar content')}\n"
        formatted += f"Themes: {metadata.get('themes', 'N/A')}\n"

        # Include the essay text
        formatted += f"\nEssay Content:\n{essay['text']}\n"
        formatted += "\n" + "-" * 60 + "\n\n"

    formatted += "=== END EXAMPLES ===\n\n"
    formatted += "Use these examples to understand:\n"
    formatted += "- Effective narrative structures and openings\n"
    formatted += "- How to develop themes authentically\n"
    formatted += "- Balance of showing vs telling\n"
    formatted += "- Strong opening and closing techniques\n"
    formatted += "- Voice and tone appropriate for the target university\n"
    formatted += "\nDO NOT copy these essays - learn from their techniques and apply similar principles in fresh ways.\n"

    return formatted


def rag_retrieval_agent(state: EssayState) -> dict:
    """
    RAG Retrieval Agent - Finds similar successful essays.

    This agent runs after Profile Agent and before Brainstorm Agent.
    It searches the vector database for relevant examples that can
    inform the essay generation process.

    Args:
        state: Current pipeline state

    Returns:
        Updated state with 'retrieved_essays' and 'rag_context' fields
    """
    print("\n[RAG RETRIEVAL AGENT] Searching for similar successful essays...")

    # Get database manager
    db_manager = get_db_manager()

    # Build search query
    search_query = create_search_query(state)
    print(f"[RAG RETRIEVAL AGENT] Search query: '{search_query[:100]}...'")

    # Search vector database
    n_results = 5
    min_score = 7.5

    results = db_manager.search_similar_essays(
        query=search_query,
        n_results=n_results * 2  # Get more than needed for filtering
    )

    # Filter by score
    filtered_results = [
        r for r in results
        if r['metadata'].get('score', 0) >= min_score
    ][:n_results]  # Take top N after filtering

    # Add retrieval reasoning
    for result in filtered_results:
        result['why_retrieved'] = explain_retrieval(result, state)

    # Format for agents
    rag_context = format_retrieved_essays(filtered_results, state)

    print(f"[RAG RETRIEVAL AGENT] Retrieved {len(filtered_results)} high-quality examples")
    for i, essay in enumerate(filtered_results, 1):
        metadata = essay.get('metadata', {})
        print(f"  {i}. {metadata.get('student', 'Unknown')} - "
              f"{metadata.get('university', 'N/A')} - "
              f"Score: {metadata.get('score', 'N/A')} - "
              f"Similarity: {essay['similarity']:.3f}")

    return {
        "retrieved_essays": filtered_results,
        "rag_context": rag_context,
        "current_agent": "brainstorm"
    }


# Test function
def test_retrieval_agent():
    """
    Test the RAG retrieval agent.

    Usage:
        python -m agents.rag_retrieval_agent
    """
    print("\n=== TESTING RAG RETRIEVAL AGENT ===\n")

    # Mock state (simulating what Profile Agent would produce)
    test_state: EssayState = {
        'prompt': "Write about how learning to code changed your perspective on problem-solving",
        'student_profile': {
            'name': 'Test Student',
            'background': 'First-generation college student passionate about technology',
            'interests': {'academic': 'Computer Science', 'personal': 'Building apps'}
        },
        'target_university': 'MIT',
        'profile_analysis': 'Student has strong technical background with focus on coding and problem-solving',
        'current_agent': 'rag'
    }

    # Run retrieval
    result = rag_retrieval_agent(test_state)

    # Show results
    print("\n=== RAG CONTEXT (first 1000 chars) ===\n")
    print(result['rag_context'][:1000] + "...\n")

    print("\n[RAG RETRIEVAL AGENT] Test complete!")


if __name__ == "__main__":
    test_retrieval_agent()
