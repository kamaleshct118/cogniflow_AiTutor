"""
===============================================================================
 SYNAPSE BACKEND — Master LangGraph Topology & Routing (graph.py)
===============================================================================
 Purpose:
   • Defines the master state graph connecting all 8 specialized agents and
     utility nodes with deterministic conditional routing.

 Core Logic & Hierarchy:
   ├── START ──► Agent 3A (Validator) ──► Agent 5 (Scope Guardrail)
   ├── Guardrail Router (route_from_guardrail):
   │     ├── trigger_gap_analysis == True ──► Agent 3B (Gap Analyzer) ──► END
   │     ├── is_off_topic == True         ──► Agent 4 (Teacher Alert) ──► END
   │     ├── requires_deep_research == True ──► Agent 2 (Wavelength Setter)
   │     └── Default / Fast Path           ──► Agent 4 (Mentality Teacher)
   ├── Agent 2 ──► Agent 6 (Researcher) ──► Agent 4 (Mentality Teacher)
   └── Teacher Router (route_from_teacher):
         ├── Fallback Research Needed (Max 2) ──► Loop to Agent 2
         └── Finalized Response              ──► Memory Compressor ──► END
===============================================================================
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import os
import sqlite3
from state import SyntapseChamberState
from nodes import guardrail_node, research_node, teacher_node, cognitive_validator_node, gap_analyzer_node, memory_compressor_node, wavelength_setter_node, quality_critic_node

# --- CONDITIONAL ROUTING FUNCTIONS ---

def route_from_guardrail(state: SyntapseChamberState) -> str:
    """
    Decides the next step after the Guardrail (Agent 5) evaluates the user input.
    """
    # 1. If FAB button was clicked, run the Gap Analyzer
    if state.get("trigger_gap_analysis"):
        return "gap_analyzer"
    
    # 2. If the user tried to pivot to an off-topic domain, send straight to teacher for rejection
    if state.get("is_off_topic"):
        return "teacher"
        
    # 3. If the question is in-bounds but highly complex, trigger deep research
    if state.get("requires_deep_research"):
        return "wavelength_setter"
        
    # 4. Standard path: go straight to teacher
    return "teacher"

def route_from_teacher(state: SyntapseChamberState) -> str:
    """
    Decides if the Teacher needs to loop back to the Researcher or move to Quality Critic.
    """
    if state.get("requires_deep_research"):
        attempts = state.get("research_attempts", 0)
        if attempts < 2:
            return "wavelength_setter"
    return "quality_critic"

def route_from_quality_check(state: SyntapseChamberState) -> str:
    """
    Decides if Teacher draft passed Quality Critic audit or requires a rewrite pass.
    Enforces Max-1 rewrite loop.
    """
    critique = state.get("quality_critique")
    regeneration_count = state.get("quality_regeneration_count", 0)
    
    if critique and regeneration_count <= 2:
        print(f" 🔀 [ROUTER: QUALITY CHECK] ❌ Draft Failed Audit. Redraft Pass {regeneration_count} triggered. Routing back to Agent 4 (Teacher)...")
        return "teacher"
    
    print(f" 🔀 [ROUTER: QUALITY CHECK] ✅ Draft Approved! Proceeding to END (Memory Compressor now runs async)...")
    return END

# --- BUILD THE LANGGRAPH ---

def build_syntapse_graph() -> StateGraph:
    """
    Constructs the Master LangGraph for the Syntapse Chamber Session.
    """
    # 1. Initialize Graph with our strict State Schema
    builder = StateGraph(SyntapseChamberState)

    # 2. Add all Agent Nodes
    builder.add_node("cognitive_validator", cognitive_validator_node) # Agent 3A (runs first)
    builder.add_node("guardrail", guardrail_node)         # Agent 5
    builder.add_node("wavelength_setter", wavelength_setter_node) # Agent 2
    builder.add_node("researcher", research_node)         # Agent 6
    builder.add_node("teacher", teacher_node)             # Agent 4
    builder.add_node("quality_critic", quality_critic_node) # Agent 3C
    builder.add_node("memory_compressor", memory_compressor_node) # Utility
    builder.add_node("gap_analyzer", gap_analyzer_node)   # FAB Logic

    # 3. Define the Control Flow Edges
    
    # Fan-out: Start both Cognitive Validator and Guardrail concurrently
    builder.add_edge(START, "cognitive_validator")
    builder.add_edge(START, "guardrail")
    
    # Cognitive Validator terminates its branch after updating the profile
    builder.add_edge("cognitive_validator", END)

    # Guardrail conditionally routes to the appropriate next agent
    builder.add_conditional_edges(
        "guardrail",
        route_from_guardrail,
        {
            "gap_analyzer": "gap_analyzer", # for manual trigger
            "wavelength_setter": "wavelength_setter",
            "teacher": "teacher"
        }
    )

    # Wavelength Setter builds search plans and passes to Researcher
    builder.add_edge("wavelength_setter", "researcher")

    # If Researcher (Agent 6) is called, it hands off to Teacher to generate response
    builder.add_edge("researcher", "teacher")
    
    # The Teacher evaluates if it needs fallback research. If not, it hands off to Quality Critic (Agent 3C).
    builder.add_conditional_edges(
        "teacher",
        route_from_teacher,
        {
            "wavelength_setter": "wavelength_setter",
            "quality_critic": "quality_critic"
        }
    )

    # Quality Critic audits Teacher draft: loops back to Teacher on FAIL, or proceeds to END on PASS
    builder.add_conditional_edges(
        "quality_critic",
        route_from_quality_check,
        {
            "teacher": "teacher",
            END: END
        }
    )

    # Cognitive Validator is NOT a terminal node if it's the start node. 
    # But if manually triggered by the FAB, it can act as a loop. We handle manual triggers securely.
    
    # Gap Analyzer is a terminal node for the cycle
    builder.add_edge("gap_analyzer", END)

    # Compile the graph with persistent SQLite checkpointer (survives server restarts)
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "db"))
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "syntapse_sessions.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    graph = builder.compile(checkpointer=memory)
    
    return graph

# Export the compiled graph instance
syntapse_app = build_syntapse_graph()
