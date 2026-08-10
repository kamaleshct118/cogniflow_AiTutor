import sys
import io
import os
import time
import uuid
from pprint import pprint
from graph import syntapse_app
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv()

load_dotenv()

def print_node_activity(node_name, state_update, elapsed_time):
    print(f"\n   [LAYER TRIGGERED]: {node_name.upper()} (Took {elapsed_time:.2f}s)")
    if state_update is None:
        return
    for key, value in state_update.items():
        if key == "messages":
            last_msg = value[-1] if isinstance(value, list) else value
            content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            print(f"\n      --- [AI RESPONSE ({node_name.upper()})] ---\n      {content}\n      ---------------------------\n")
        elif key == "research_catalog":
            import json
            print(f"      -> Research Catalog Appended with New Facts:\n{json.dumps(value, indent=2)}")
        elif type(value) == bool:
            print(f"      -> Control Flag {key}: {value}")

def simulate_chat_turn(config, user_message_text=None, trigger_gap=False):
    """Simulates a single conversational turn using LangGraph persistence."""
    current_state = syntapse_app.get_state(config).values
    next_turn = current_state.get("turn_id", 0) + 1
    
    input_state = {
        "turn_id": next_turn,
        "request_id": f"REQ_{uuid.uuid4().hex[:8]}"
    }
    
    if user_message_text:
        print(f"\n[USER SAYS]: {user_message_text}")
        input_state["messages"] = [HumanMessage(content=user_message_text)]
    
    if trigger_gap:
        print(f"\n[UI ACTION]: User clicked 'Analyze Knowledge Gaps' (FAB)")
        input_state["trigger_gap_analysis"] = True

    print("-" * 70)
    
    turn_start_time = time.time()
    last_node_time = turn_start_time
    
    # Stream through the LangGraph architecture using delta input
    for output in syntapse_app.stream(input_state, config=config):
        current_time = time.time()
        node_elapsed = current_time - last_node_time
        
        for node_name, state_update in output.items():
            print_node_activity(node_name, state_update, node_elapsed)
                    
        last_node_time = time.time() # Reset clock for next node
        
    total_turn_time = time.time() - turn_start_time
    print(f"\n   [TURN COMPLETE] Total Latency: {total_turn_time:.2f}s")
    print("-" * 70)
    
    return syntapse_app.get_state(config).values

# =====================================================================
from orchestrator import run_pre_chamber_agents

# =====================================================================
# =====================================================================
# SCENARIO: TEACHER REFINEMENT (3 Depth Levels)
# =====================================================================
def scenario_teacher_refinement(cognitive_profile):
    print("\n" + "="*80)
    print("🚀 SCENARIO: TEACHER REFINEMENT (Testing Agent 4 Intelligence)")
    print("="*80)
    
    topic = "Docker Containerization"
    user_context = "I know that Docker packages applications into containers so they run the same everywhere, but I want to dive deep into internals."
    
    state = {
        "session_id": "TEST_SESSION_TEACHER",
        "turn_id": 1,
        "request_id": f"REQ_INIT_DOC",
        "cognitive_profile": cognitive_profile,
        "topic_name": topic,
        "messages": [SystemMessage(content=f"Context provided by user:\n{user_context}")],
        "research_id": None,
        "research_catalog": [],
        "discussed_concepts": [],
        "requires_deep_research": False,
        "research_attempts": 0,
        "trigger_gap_analysis": False,
        "is_off_topic": False,
        "search_plan": None,
        "active_cognitive_hypotheses": {},
        "last_teacher_probe": None,
        "cognitive_events": [],
        "last_validation": None
    }
    
    config = {"recursion_limit": 15, "configurable": {"thread_id": state["session_id"]}}
    
    # Initialize the state in the checkpointer
    syntapse_app.update_state(config, state)
    
    # Turn 1: Simple
    state = simulate_chat_turn(config, "What is a Docker container?")
    
    # Turn 2: Natural Connection
    state = simulate_chat_turn(config, "Why does it need namespaces?")

    # Turn 3: Deep
    state = simulate_chat_turn(config, "Okay, now explain exactly what happens when I run docker run nginx.")
    
    # Turn 4: Answer the Socratic Probe from Turn 3
    # We will simulate a user attempting to reason about the mechanism
    state = simulate_chat_turn(config, "I think when you run docker run nginx, it uses the daemon to pull the image and then sets up the namespaces before starting the process inside them.")

if __name__ == "__main__":
    # Simulate Frontend reading the calibration file (topic1.md)
    try:
        with open(r"V:\PROJECTS\project_agents\test_chamber\topic1.md", "r", encoding="utf-8") as f:
            modal_answers = f.read().strip()
    except Exception:
        modal_answers = "I usually build pipelines by starting with the data source..."
        
    # Phase 0: Load the Chamber ONCE (Gets the Cognitive Profile)
    # This prevents us from waiting for the 70B model to parse the huge essay 3 times.
    print("Loading Pre-Chamber AI Profile once...")
    profile = run_pre_chamber_agents(modal_answers, "Docker Containerization")
    
    # Run the Teacher Refinement scenario
    scenario_teacher_refinement(profile)
