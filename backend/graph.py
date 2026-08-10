from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from state import SyntapseChamberState
from nodes import guardrail_node, research_node, teacher_node, cognitive_validator_node, gap_analyzer_node, memory_compressor_node, wavelength_setter_node

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
        
    # 4. Standard path: go straight to teacher (we compress memory AFTER the teacher speaks now)
    return "teacher"

def route_from_teacher(state: SyntapseChamberState) -> str:
    """
    Decides if the Teacher needs to loop back to the Researcher.
    """
    if state.get("requires_deep_research"):
        attempts = state.get("research_attempts", 0)
        if attempts < 2:
            return "wavelength_setter"
    return "memory_compressor"

# --- BUILD THE LANGGRAPH ---

def build_syntapse_graph() -> StateGraph:
    """
    Constructs the Master LangGraph for the Syntapse Chamber Session.
    """
    # 1. Initialize Graph with our strict State Schema
    builder = StateGraph(SyntapseChamberState)

    # 2. Add all Agent Nodes
    builder.add_node("cognitive_validator", cognitive_validator_node) # Agent 3 (runs first)
    builder.add_node("guardrail", guardrail_node)         # Agent 5
    builder.add_node("wavelength_setter", wavelength_setter_node) # Agent 2
    builder.add_node("researcher", research_node)         # Agent 6
    builder.add_node("memory_compressor", memory_compressor_node) # Utility
    builder.add_node("teacher", teacher_node)             # Agent 4
    builder.add_node("gap_analyzer", gap_analyzer_node)   # FAB Logic

    # 3. Define the Control Flow Edges
    
    # Every chat turn starts at the Cognitive Validator to check if the user is answering a probe
    builder.add_edge(START, "cognitive_validator")
    
    # After validation, it flows to Guardrail
    builder.add_edge("cognitive_validator", "guardrail")

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
    
    # The Teacher evaluates if it needs fallback research. If not, it hands off to Memory Compressor for background cleanup.
    builder.add_conditional_edges(
        "teacher",
        route_from_teacher,
        {
            "wavelength_setter": "wavelength_setter",
            "memory_compressor": "memory_compressor"
        }
    )

    # Memory Compressor cleans state and then ENDS the turn
    builder.add_edge("memory_compressor", END)

    # Cognitive Validator is NOT a terminal node if it's the start node. 
    # But if manually triggered by the FAB, it can act as a loop. We handle manual triggers securely.
    
    # Gap Analyzer is a terminal node for the cycle
    builder.add_edge("gap_analyzer", END)

    # Compile the graph with persistent SQLite checkpointer (survives server restarts)
    conn = sqlite3.connect("./syntapse_sessions.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    graph = builder.compile(checkpointer=memory)
    
    return graph

# Export the compiled graph instance
syntapse_app = build_syntapse_graph()
