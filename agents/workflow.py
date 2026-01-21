"""
Multi-Agent Essay Generation Workflow
Enhanced with RAG (Retrieval-Augmented Generation)

Flow: Profile → RAG Retrieval → Research → Brainstorm → Outline → Draft → Critique
"""

from langgraph.graph import StateGraph, END
from agents.state import EssayState

# Import all agents
from agents.profile_agent import profile_agent
from agents.rag_retrieval_agent import rag_retrieval_agent  # NEW - RAG Agent
from agents.research_agent import research_agent
from agents.brainstorm_agent import brainstorm_agent
from agents.outline_agent import outline_agent
from agents.draft_agent import draft_agent
from agents.critique_agent import critique_agent


def create_essay_workflow():
    """
    Creates the complete 7-agent workflow with RAG retrieval.

    Flow: Profile → RAG → Research → Brainstorm → Outline → Draft → Critique

    The RAG agent retrieves similar successful essays from the vector database
    to provide context for the brainstorm and outline agents.
    """

    workflow = StateGraph(EssayState)

    # Add all agents as nodes
    workflow.add_node("profile", profile_agent)           # Agent 0 - Profile analysis
    workflow.add_node("rag", rag_retrieval_agent)         # Agent 1 - RAG retrieval (NEW)
    workflow.add_node("research", research_agent)         # Agent 2 - Prompt analysis
    workflow.add_node("brainstorm", brainstorm_agent)     # Agent 3 - Idea generation
    workflow.add_node("outline", outline_agent)           # Agent 4 - Structure
    workflow.add_node("draft", draft_agent)               # Agent 5 - Writing
    workflow.add_node("critique", critique_agent)         # Agent 6 - Feedback

    # Define linear flow
    workflow.set_entry_point("profile")
    workflow.add_edge("profile", "rag")        # Profile → RAG (retrieve examples)
    workflow.add_edge("rag", "research")       # RAG → Research
    workflow.add_edge("research", "brainstorm")
    workflow.add_edge("brainstorm", "outline")
    workflow.add_edge("outline", "draft")
    workflow.add_edge("draft", "critique")
    workflow.add_edge("critique", END)

    return workflow.compile()


def create_essay_workflow_without_rag():
    """
    Creates the workflow WITHOUT RAG for comparison/testing.

    Flow: Profile → Research → Brainstorm → Outline → Draft → Critique
    """

    workflow = StateGraph(EssayState)

    workflow.add_node("profile", profile_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("brainstorm", brainstorm_agent)
    workflow.add_node("outline", outline_agent)
    workflow.add_node("draft", draft_agent)
    workflow.add_node("critique", critique_agent)

    workflow.set_entry_point("profile")
    workflow.add_edge("profile", "research")
    workflow.add_edge("research", "brainstorm")
    workflow.add_edge("brainstorm", "outline")
    workflow.add_edge("outline", "draft")
    workflow.add_edge("draft", "critique")
    workflow.add_edge("critique", END)

    return workflow.compile()

def run_essay_generation(
    prompt: str,
    student_profile: dict,
    target_university: str,
    essay_type: str = "common_app",
    word_count: int = 650,
    other_essays: list = None
) -> dict:
    """
    Convenience function to run complete workflow
    
    Args:
        prompt: Essay prompt
        student_profile: Student's background and experiences
        target_university: Target school (MIT, Harvard, etc.)
        essay_type: Type of essay (common_app, supplement_1, etc.)
        word_count: Target word count
        other_essays: Other essays in this application suite
    
    Returns:
        Final state with essay and critique
    """
    
    workflow = create_essay_workflow()
    
    initial_state: EssayState = {
        "prompt": prompt,
        "student_profile": student_profile,
        "target_university": target_university,
        "essay_type": essay_type,
        "word_count": word_count,
        "other_essays_in_suite": other_essays or [],
        "current_agent": "profile"
    }
    
    result = workflow.invoke(initial_state)

    return result


def run_essay_generation_without_rag(
    prompt: str,
    student_profile: dict,
    target_university: str,
    essay_type: str = "common_app",
    word_count: int = 650,
    other_essays: list = None
) -> dict:
    """
    Run essay generation WITHOUT RAG for comparison testing.

    Args:
        prompt: Essay prompt
        student_profile: Student's background and experiences
        target_university: Target school (MIT, Harvard, etc.)
        essay_type: Type of essay (common_app, supplement_1, etc.)
        word_count: Target word count
        other_essays: Other essays in this application suite

    Returns:
        Final state with essay and critique
    """

    workflow = create_essay_workflow_without_rag()

    initial_state: EssayState = {
        "prompt": prompt,
        "student_profile": student_profile,
        "target_university": target_university,
        "essay_type": essay_type,
        "word_count": word_count,
        "other_essays_in_suite": other_essays or [],
        "current_agent": "profile"
    }

    result = workflow.invoke(initial_state)

    return result