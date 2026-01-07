from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class EssayState(TypedDict):
    """
    State that flows through all agents.
    Each agent reads from and writes to this state.
    """
    # Input from user
    prompt: str
    user_context: Optional[str]  # Optional background about the student
    
    # Agent outputs (populated as workflow progresses)
    research_analysis: str      # Research Agent output
    brainstorm_ideas: List[str] # Brainstorm Agent output (5 ideas)
    selected_idea: str          # Which idea was chosen
    essay_outline: str          # Outline Agent output
    essay_draft: str            # Draft Agent output (the actual essay)
    essay_critique: str         # Critique Agent output
    
    # Metadata
    current_agent: str          # Which agent is currently working
    agent_times: dict           # Track how long each agent takes
    messages: Annotated[List[BaseMessage], operator.add]  # Agent communication log