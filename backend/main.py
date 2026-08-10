import os
import json
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from graph import syntapse_app
from orchestrator import live_agent_1_mapper

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("syntapse.api")

app = FastAPI(
    title="Syntapse Chamber API",
    description="Backend API powering the Syntapse Persistent Cognitive Profiling & Multi-Agent Orchestration System",
    version="1.0.0"
)

# Enable CORS for local testing with the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---

class CalibrationRequest(BaseModel):
    modal_text: str

class CalibrationResponse(BaseModel):
    status: str
    cognitive_profile: Dict[str, Any]

class SessionStartRequest(BaseModel):
    session_id: str
    topic_name: str
    cognitive_profile: Dict[str, Any]
    user_context: Optional[str] = None

class SessionStartResponse(BaseModel):
    status: str
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    cognitive_profile: Optional[Dict[str, Any]] = None


class GapAnalysisRequest(BaseModel):
    session_id: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    probe: Optional[Dict[str, Any]] = None
    depth: Optional[str] = None
    agents_triggered: Optional[List[str]] = None  # FIX #6: Real telemetry

class GapAnalysisResponse(BaseModel):
    session_id: str
    diagnostic_summary: str
    suggestions: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    version: str

# --- Utility & Health Endpoints ---

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for checking API status.
    """
    return HealthResponse(status="online", version="1.0.0")

# --- Pre-Chamber Endpoints ---

@app.post("/calibrate", response_model=CalibrationResponse)
async def calibrate_user(request: CalibrationRequest):
    """
    Phase 0: Runs Agent 1 (Mapper) to analyze the user's calibration essay 
    and output their structural Cognitive Profile.
    """
    print("\n" + "="*60)
    print(" 📥 [POST /calibrate] User Calibration Request Received")
    print(f" 📄 User Essay ({len(request.modal_text)} chars): \"{request.modal_text[:120]}...\"")
    print("="*60)
    try:
        profile = await run_in_threadpool(live_agent_1_mapper, request.modal_text)
        print(" 🗺️  [AGENT 1 - MAPPER] Full Extracted Cognitive Profile JSON:")
        print(json.dumps(profile, indent=2))
        print("="*60 + "\n")
        return CalibrationResponse(status="success", cognitive_profile=profile)
    except Exception as e:
        logger.error(f"Error in /calibrate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/calibrate")
async def delete_cognitive_profile():
    """
    Deletes/resets the active cognitive footprint profile for testing.
    """
    print("\n" + "="*60)
    print(" 🗑️  [DELETE /calibrate] Cognitive Footprint Profile Reset Requested")
    print("="*60 + "\n")
    return {"status": "success", "message": "Cognitive profile deleted successfully."}

@app.post("/session/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """
    Phase 0 -> Phase 1: Initializes the persistent LangGraph state checkpointer 
    for the session using the previously generated Cognitive Profile.
    """
    print("\n" + "="*60)
    print(f" 🚀 [POST /session/start] Initializing Chamber Session: {request.session_id}")
    print(f" 📌 Topic: \"{request.topic_name}\"")
    if request.cognitive_profile:
        import json
        print(" 🧠 [FRONTEND HYDRATION] Received persistent Cognitive Profile from client:")
        print(json.dumps(request.cognitive_profile, indent=2))
    print("="*60 + "\n")
    config = {"configurable": {"thread_id": request.session_id}}
    
    state = {
        "session_id": request.session_id,
        "turn_id": 1,
        "request_id": "REQ_INIT",
        "cognitive_profile": request.cognitive_profile,
        "topic_name": request.topic_name,
        "user_topic_context": request.user_context,  # Stored as first-class field, not a SystemMessage
        "messages": [],
        "research_catalog": [],
        "teacher_memory": [],
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
    
    try:
        await run_in_threadpool(syntapse_app.update_state, config, state)
        return SessionStartResponse(status="success", session_id=request.session_id)
    except Exception as e:
        logger.error(f"Error in /session/start: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Active Chamber Endpoints ---

@app.get("/session/{session_id}")
async def get_session_state(session_id: str):
    """
    Retrieves the current state and messages of an active chamber session.
    Useful for frontend state restoration/hydration upon page refresh.
    """
    config = {"configurable": {"thread_id": session_id}}
    try:
        current_state = await run_in_threadpool(syntapse_app.get_state, config)
        if not current_state or not current_state.values:
            raise HTTPException(status_code=404, detail="Session state not found.")
            
        values = current_state.values
        messages = [
            {"role": "user" if isinstance(m, HumanMessage) else "ai", "content": str(m.content)}
            for m in values.get("messages", [])
            if not isinstance(m, SystemMessage)
        ]
        
        return {
            "session_id": session_id,
            "topic_name": values.get("topic_name"),
            "messages": messages,
            "cognitive_profile": values.get("cognitive_profile"),
            "last_teacher_probe": values.get("last_teacher_probe")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Phase 1: Processes a single chat turn through the Syntapse Multi-Agent graph.
    """
    print("\n" + "="*60)
    print(f" 💬 [POST /chat] Session: {request.session_id}")
    print(f" 💬 User Input: \"{request.message}\"")
    print("="*60)
    config = {"recursion_limit": 15, "configurable": {"thread_id": request.session_id}}
    
    try:
        current_state = await run_in_threadpool(syntapse_app.get_state, config)
        if not current_state or not current_state.values:
            raise HTTPException(status_code=400, detail="Session state not found. Call /session/start first.")
            
        # Update cognitive profile in the session state if provided in the chat request
        if request.cognitive_profile and "tutor_directive" in request.cognitive_profile:
            print(" 🧠 [STATE SYNCHRONIZATION] Updating session state with client's active Cognitive Profile")
            await run_in_threadpool(
                syntapse_app.update_state,
                config,
                {"cognitive_profile": request.cognitive_profile}
            )
            
        result = await run_in_threadpool(
            syntapse_app.invoke,
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )
        
        messages = result.get("messages", [])
        response_msg = ""
        if messages:
            response_msg = str(messages[-1].content)
            
        last_teacher_res = result.get("last_teacher_response") or {}
        probe = result.get("last_teacher_probe")
        
        # FIX #6: Build real agent telemetry from actual result state flags
        agents_triggered = ["Agent 5 (Guardrail)"]
        if result.get("research_attempts", 0) > (current_state.values.get("research_attempts") or 0):
            agents_triggered.append("Agent 2 (Wavelength Setter)")
            agents_triggered.append("Agent 6 (Researcher)")
        if not result.get("is_greeting") and not result.get("is_meta"):
            agents_triggered.append("Agent 4 (Teacher)")
        
        print(" 🧑‍🏫 [AGENT 4 - TEACHER RESPONSE GENERATED]")
        print(f"    • Response Length: {len(response_msg)} chars")
        print(f"    • Depth Level    : {last_teacher_res.get('explanation_depth', 'Deep')}")
        print(f"    • Agents Triggered: {agents_triggered}")
        if probe:
            print(" 🎯 [SOCRATIC PROBE CREATED]")
            print(f"    • Target Concept : {probe.get('target_concept')}")
            print(f"    • Probe Question : \"{probe.get('question')}\"")
        print("="*60 + "\n")
        
        return ChatResponse(
            session_id=request.session_id,
            message=response_msg,
            probe=probe,
            depth=last_teacher_res.get("explanation_depth"),
            agents_triggered=agents_triggered
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Deletes a specific learning chamber from the SQLite checkpointer database.
    """
    print("\n" + "="*60)
    print(f" 🗑️  [DELETE /session/{session_id}] Chamber Wipe Requested")
    try:
        import sqlite3
        conn = sqlite3.connect("./syntapse_sessions.db")
        cursor = conn.cursor()
        # Delete from both langgraph tables
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (session_id,))
        cursor.execute("DELETE FROM writes WHERE thread_id = ?", (session_id,))
        conn.commit()
        conn.close()
        print("   ✅ Chamber successfully purged from database.")
    except Exception as e:
        logger.error(f"Error deleting session {session_id} from DB: {e}")
        raise HTTPException(status_code=500, detail="Database deletion failed.")
    print("="*60 + "\n")
    return {"status": "success"}

@app.post("/gap_analysis", response_model=GapAnalysisResponse)
async def trigger_gap_analysis(request: GapAnalysisRequest):
    """
    FAB Button: Interrupts the chat flow to execute Agent 3B (Gap Analyzer)
    based on the current conversational history.
    """
    print("\n" + "="*60)
    print(f" 🔍 [POST /gap_analysis] Triggering Diagnostic Gap Analysis for Session: {request.session_id}")
    print("="*60)
    config = {"recursion_limit": 15, "configurable": {"thread_id": request.session_id}}
    
    try:
        current_state = await run_in_threadpool(syntapse_app.get_state, config)
        if not current_state or not current_state.values:
            raise HTTPException(status_code=400, detail="Session state not found.")
            
        await run_in_threadpool(syntapse_app.update_state, config, {"trigger_gap_analysis": True})
        
        result = await run_in_threadpool(
            syntapse_app.invoke,
            {"messages": [HumanMessage(content="[SYSTEM: RUN GAP ANALYSIS]")]},
            config=config
        )
        
        gap_data = result.get("last_gap_analysis", {})
        
        print(" 🔍 [AGENT 3B - GAP DIAGNOSTIC COMPLETE]")
        print(f"    • Summary: \"{gap_data.get('diagnostic_summary', '')[:100]}...\"")
        print(f"    • Suggestions Count: {len(gap_data.get('suggestions', []))}")
        print("="*60 + "\n")
        
        return GapAnalysisResponse(
            session_id=request.session_id,
            diagnostic_summary=gap_data.get("diagnostic_summary", "No summary generated."),
            suggestions=gap_data.get("suggestions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /gap_analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

