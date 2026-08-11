"""
===============================================================================
 SYNAPSE BACKEND — LangGraph Shared State Blackboard (state.py)
===============================================================================
 Purpose:
   • Defines SyntapseChamberState schema and annotated list reducers for
     thread-safe multi-agent state management.

 Core Logic & Hierarchy:
   ├── messages          : Annotated[list, add_messages] (Append-only conversation history)
   ├── research_catalog  : Annotated[list, append_research] (Background web facts)
   ├── teacher_memory    : Annotated[list, append_research] (1KB ghost explanation records)
   ├── cognitive_events  : Annotated[list, append_research] (Immutable probe audit trail)
   ├── cognitive_profile : Bayesian confidence weights dictionary
   └── Orchestration Flags: Routing booleans (requires_deep_research, is_off_topic, etc.)
===============================================================================
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from schemas import CognitiveProfilePayload, ScopeSizerPayload, ResearchPayload, TeacherProbe
from cognitive.profile_schema import CognitiveEvent, CognitiveValidationPayload, HypothesisState

# Reducer function to append to lists rather than overwrite
def append_research(left: List[Any], right: List[Any]) -> List[Any]:
    if left is None:
        return right
    if right is None:
        return left
    return left + right

class SyntapseChamberState(TypedDict):
    """
    The Master LangGraph State Object for a Single Topic Chamber.
    Maintains strict separation between conversational messages and raw research data.
    """
    
    # --- 1. GLOBAL SETTINGS ---
    session_id: str
    turn_id: int
    request_id: str
    
    # The user's cognitive DNA extracted by Agent 1. Stays persistent across the session.
    cognitive_profile: Optional[CognitiveProfilePayload]
    
    # Target topic context (e.g., "Transformer Architecture")
    topic_name: str
    
    # What the user already knows / plans to study about THIS topic (from the topic input box).
    # Persists for the entire session — never scrolls off like a SystemMessage would.
    user_topic_context: Optional[str]
    
    # --- 2. THE CLEAN CONVERSATION STREAM ---
    # Human-facing chat history (User questions, Teacher responses)
    # add_messages reducer automatically appends new messages to the list
    messages: Annotated[list, add_messages]
    
    # --- 3. THE ISOLATED RESEARCH CATALOG ---
    # Background datastore where Agent 6 dumps scraped facts and code snippets.
    # The append_research reducer ensures new facts are added, not overwritten.
    research_id: Optional[str]
    research_catalog: Annotated[List[dict], append_research]
    
    # Compressed semantic teaching history
    teacher_memory: Annotated[List[dict], append_research]
    
    # Tracking concepts mastered during this session
    discussed_concepts: List[str]
    
    # --- 4. ORCHESTRATION FLAGS ---
    # Set by Guardrail or FAB UI to trigger specific routing paths
    requires_deep_research: bool
    research_attempts: int
    trigger_gap_analysis: bool
    is_off_topic: bool
    is_greeting: bool
    is_meta: bool
    search_plan: Optional[dict]
    
    # --- 5. COGNITIVE FEEDBACK LOOP & QUALITY AUDIT ---
    # Tracks the longitudinal hypothesis testing loop and quality critic state
    active_cognitive_hypotheses: Dict[str, dict]
    last_teacher_probe: Optional[dict]
    last_teacher_response: Optional[dict]
    quality_critique: Optional[str]
    quality_evaluation: Optional[dict]
    quality_actionable_feedback: Optional[dict]
    quality_regeneration_count: int
    cognitive_events: Annotated[List[dict], append_research]
    last_validation: Optional[dict]
    last_gap_analysis: Optional[dict]
