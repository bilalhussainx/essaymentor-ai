"""
State definitions for multi-agent essay workflow
"""

from typing import TypedDict, List, Optional, Dict

class StudentProfile(TypedDict, total=False):
    """Student background information for personalized essays"""
    
    # Identity
    student_id: str
    name: str
    age: Optional[int]
    background: str
    identity: str
    location: str
    
    # Family context
    family: Dict[str, str]
    socioeconomic: Optional[str]
    languages: List[str]
    
    # Experiences (the material they have to work with)
    major_experiences: List[Dict[str, str]]  # Main experiences to draw from
    activities: List[str]
    achievements: List[str]
    
    # Academic/Intellectual
    interests: Dict[str, str]
    gpa: Optional[float]
    sat_verbal: Optional[int]
    intellectual_profile: Optional[str]
    
    # Writing characteristics
    voice_characteristics: Dict[str, str]
    vocabulary_level: Optional[str]
    writing_style: Optional[str]
    
    # Consistency tracking
    consistent_details: Dict[str, str]  # Details to maintain (names, places, etc.)
    experiences_used: Dict[str, str]  # Track what's been used in other essays

class EssayState(TypedDict, total=False):
    """State passed through the multi-agent workflow"""
    
    # INPUT - What we start with
    prompt: str
    word_count: int  # Target word count (650 for common app, varies for supplements)
    
    # PERSONALIZATION CONTEXT - NEW
    student_profile: StudentProfile
    target_university: str  # MIT, Harvard, Stanford, etc.
    essay_type: str  # 'common_app', 'supplement_1', 'supplement_2', etc.
    other_essays_in_suite: List[Dict]  # Other essays in this application
    
    # AGENT OUTPUTS
    # Profile Agent (Agent 0) - NEW
    profile_analysis: str  # Detailed analysis of which experiences to use
    selected_experiences: str  # Experiences selected for this essay
    university_alignment: str  # How student aligns with university
    
    # RAG Retrieval Agent - Retrieved successful essay examples
    retrieved_essays: List[Dict]  # Similar essays from vector database
    rag_context: str  # Formatted context for other agents

    # Research Agent (Agent 1)
    prompt_type: str
    prompt_analysis: str
    
    # Brainstorm Agent (Agent 2)
    ideas: str
    essay_approach: str
    
    # Outline Agent (Agent 3)
    essay_outline: str
    
    # Draft Agent (Agent 4)
    essay_draft: str
    
    # Critique Agent (Agent 5)
    critique: str
    final_essay: str
    
    # WORKFLOW CONTROL
    current_agent: str  # Tracks which agent should run next