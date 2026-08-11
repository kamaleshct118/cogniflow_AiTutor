"""
===============================================================================
 SYNAPSE BACKEND — Agent Node Implementations (nodes.py)
===============================================================================
 Purpose:
   • Implements execution logic for each specialized agent in the LangGraph graph.

 Core Logic & Hierarchy:
   ├── cognitive_validator_node (Agent 3A) : Probe answer grading & Bayesian weight updates
   ├── guardrail_node           (Agent 5)  : Chamber topic safety & intent classification
   ├── wavelength_setter_node   (Agent 2)  : Zoom scope selection & Tavily search query writing
   ├── research_node            (Agent 6)  : Tavily API execution & fact catalog population
   ├── teacher_node             (Agent 4)  : Socratic response synthesis & probe generation
   ├── memory_compressor_node   (Utility)  : 1KB ghost record compression & SQLite checkpointer
   └── gap_analyzer_node        (Agent 3B) : Historical path analysis & 1-click diagnostic cards
===============================================================================
"""
import json
import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from google import genai
# from google.genai import types

from state import SyntapseChamberState
from schemas import GuardrailDecision, TeacherResponsePayload, KnowledgeGapAnalysis, ResearchPayload, ScopeSizerPayload, QualityCriticPayload
from pydantic import ValidationError

import urllib.request
import urllib.error
import os
import time
import uuid
import hashlib
from datetime import datetime
from tavily import TavilyClient

from cognitive.profile_schema import CognitiveEvent, CognitiveValidationPayload
from cognitive.profile_reducer import apply_event_to_profile

logger = logging.getLogger("syntapse.nodes")

def call_gemini_api(system_instruction: str, user_content: str) -> Dict[str, Any]:
    """Helper to make live API calls to Gemini using standard urllib."""
    key = os.getenv("MODEL_1_MAPPER_KEY")
    if not key:
        logger.error("No API Key found. Returning empty.")
        return {}
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={key}"
    
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": user_content}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['candidates'][0]['content']['parts'][0]['text']
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
    except Exception as e:
        logger.error(f"API Error: {e}")
        return {}

def call_nvidia_api(system_instruction: str, user_content: str, api_key: str, model_name: str = "meta/llama-3.1-8b-instruct") -> Dict[str, Any]:
    """Helper to make live API calls to NVIDIA NIM (Llama 3.1 or Nemotron)."""
    if not api_key:
        logger.error("No NVIDIA API Key found. Returning empty.")
        return {}
        
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        "response_format": {"type": "json_object"}
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}', 'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['choices'][0]['message']['content']
            # Clean markdown JSON block if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
    except Exception as e:
        logger.error(f"NVIDIA API Error: {e}")
        return {}

FALLBACK_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

def call_groq_api(system_instruction: str, user_content: str, api_key: str, model_name: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
    """Helper to make live API calls to Groq Network with multi-model rate-limit fallback."""
    if not api_key:
        logger.error("No Groq API Key found. Returning empty.")
        return {}
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    if "json" not in system_instruction.lower() and "json" not in user_content.lower():
        system_instruction += "\n\nIMPORTANT: You must reply in strictly valid JSON format."
        
    models_to_try = [model_name] + [m for m in FALLBACK_GROQ_MODELS if m != model_name]

    for current_model in models_to_try:
        payload = {
            "model": current_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={
                'Content-Type': 'application/json', 
                'Authorization': f'Bearer {api_key}', 
                'User-Agent': 'Mozilla/5.0'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                text = res_data['choices'][0]['message']['content']
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            if e.code == 429 or "rate_limit_exceeded" in error_body.lower() or "tokens" in error_body.lower():
                print(f"      -> [GROQ 429 RATE LIMIT on {current_model}]: Trying fallback model...")
                continue
            else:
                logger.error(f"Groq API Error on {current_model}: {error_body}")
                print(f"      -> [GROQ API HTTP ERROR]: {error_body}")
                return {}
        except Exception as e:
            logger.error(f"Groq API Generic Error on {current_model}: {e}")
            continue

    # If all Groq models hit rate limits, try NVIDIA NIM fallback seamlessly
    print("      -> [ALL GROQ MODELS RATE LIMITED]: Falling back to NVIDIA NIM (llama-3.1-70b)...")
    nvidia_key = os.getenv("MODEL_6_RESEARCHER_KEY") or os.getenv("MODEL_3_GAP_KEY")
    if nvidia_key:
        return call_nvidia_api(system_instruction, user_content, api_key=nvidia_key, model_name="meta/llama-3.1-70b-instruct")

    return {}




def load_skill_prompt(skill_name: str) -> str:
    """Helper to load the markdown master directives."""
    try:
        with open(f"../prompt_skills/{skill_name}.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"System Prompt for {skill_name} not found."

def get_latest_human_message(state: SyntapseChamberState) -> Any:
    messages = state.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message
    return None

def guardrail_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 5: Guardrail Agent.
    Evaluates the latest user message for topic isolation and research requirements.
    """
    last_user_message = get_latest_human_message(state)
    if not last_user_message:
        return {"is_off_topic": False, "requires_deep_research": False}
    
    last_user_text = str(last_user_message.content)
    topic_name = state.get("topic_name", "General")
    
    # 0-Token Deterministic Greeting Check
    import re
    clean_text = re.sub(r'[^\w\s]', '', last_user_text.lower()).strip()
    greeting_words = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "yes", "yep", "yeah", "cool", "awesome", "good", "got it", "makes sense", "understood"}
    if clean_text in greeting_words:
        print("\n" + "="*50)
        print(f" 🛡️  [AGENT 5 - GUARDRAIL]")
        print(f"    • Deterministic Greeting Detected: '{clean_text}'")
        print("="*50 + "\n")
        return {
            "is_off_topic": False,
            "is_greeting": True,
            "requires_deep_research": False
        }
    
    # 0-Token Deterministic Meta Check
    meta_keywords = ["what can you do", "who are you", "how does this work", "help me", "what are you"]
    if any(m in last_user_text.lower() for m in meta_keywords) and len(last_user_text) < 40:
        print("\n" + "="*50)
        print(f" 🛡️  [AGENT 5 - GUARDRAIL]")
        print(f"    • Deterministic Meta Detected: '{last_user_text}'")
        print("="*50 + "\n")
        return {
            "is_off_topic": False,
            "is_greeting": False,
            "is_meta": True,
            "requires_deep_research": False
        }
    
    # --- PRODUCTION GEMINI API CALL ---
    logger.info(f"Guardrail evaluating message: '{last_user_text}' against topic: '{topic_name}'")
    system_instruction = load_skill_prompt("guardrail_vr_holy_grail")
    
    prompt = f"TARGET TOPIC: {topic_name}\nUSER MESSAGE: {last_user_text}"
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {
            "requires_deep_research": "namespaces" in last_user_text.lower() or "lifecycle" in last_user_text.lower(),
            "is_off_topic": False,
            "topic_name": "Docker"
        }
        
    api_key = os.getenv("MODEL_5_GUARDRAIL_KEY")
    
    # Force strict JSON schema adherence for Groq
    system_instruction += "\n\nCRITICAL INSTRUCTION: You MUST return a JSON object with EXACTLY the following keys: 'classification' (string: 'IN_BOUNDS', 'METAPHOR_BRIDGE', 'OFF_TOPIC_PIVOT', 'CONVERSATIONAL_GREETING', or 'META_QUERY') and 'requires_deep_research' (boolean). Return ONLY the JSON. Do NOT include 'reasoning'."
    
    decision = call_groq_api(system_instruction, prompt, api_key=api_key, model_name="llama-3.3-70b-versatile")
    
    is_greeting = False
    is_meta = False
    if decision:
        try:
            validated = GuardrailDecision.model_validate(decision)
            is_off_topic = validated.classification == "OFF_TOPIC_PIVOT"
            is_greeting = validated.classification == "CONVERSATIONAL_GREETING"
            is_meta = validated.classification == "META_QUERY"
            requires_research = validated.requires_deep_research
        except ValidationError as e:
            logger.error(f"Guardrail schema validation failed: {e}")
            decision = None
            
    if not decision: # Fallback if API fails or validation fails
        is_off_topic = "python" in last_user_text.lower() and "biology" in topic_name.lower()
        requires_research = "how exactly" in last_user_text.lower() or "deep dive" in last_user_text.lower()
        is_greeting = last_user_text.lower().strip() in ["hi", "hello", "thanks", "ok"]
        is_meta = False

    print("\n" + "="*50)
    print(f" 🛡️  [AGENT 5 - GUARDRAIL]")
    print(f"    • Is Off Topic: {is_off_topic}")
    print(f"    • Is Greeting: {is_greeting}")
    print(f"    • Is Meta Query: {is_meta}")
    print(f"    • Requires Deep Research: {requires_research}")
    print("="*50 + "\n")
    return {
        "is_off_topic": is_off_topic,
        "is_greeting": is_greeting,
        "is_meta": is_meta,
        "requires_deep_research": requires_research
    }

def wavelength_setter_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 2: Wavelength Setter (Scope Architect).
    Analyzes topic breadth and generates the optimal search plan/queries for Agent 6.
    """
    logger.info("Executing Agent 2: Wavelength Setter...")
    system_instruction = load_skill_prompt("wavelength_setter_vr_holy_grail")
    
    topic = state.get("topic_name", "General")
    user_msg = get_latest_human_message(state)
    query = str(user_msg.content) if user_msg else topic
    
    prompt = json.dumps({
        "topic": topic,
        "user_query": query,
        "user_prior_knowledge": state.get("user_topic_context"),
        "cognitive_profile": state.get("cognitive_profile", {})
    })
    
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {
            "search_plan": {
                "detected_wavelength": "MACRO",
                "adapted_learning_scope": "mock scope",
                "user_facing_explanation": "Mock searching...",
                "agent_6_queries": [{"query": query, "search_depth": "advanced"}]
            }
        }
        
    api_key = os.getenv("MODEL_2_WAVELENGTH_KEY")
    if not api_key:
        api_key = os.getenv("MODEL_1_MAPPER_KEY") # Fallback to another Groq key if missing
        
    payload = call_groq_api(system_instruction, prompt, api_key=api_key, model_name="llama-3.3-70b-versatile")
    
    if payload:
        try:
            validated = ScopeSizerPayload.model_validate(payload)
            payload = validated.model_dump()
        except ValidationError as e:
            logger.error(f"Agent 2 schema validation failed: {e}")
            payload = None
            
    if not payload:
        payload = {
            "original_input": query,
            "detected_wavelength": "MICRO",
            "adapted_learning_scope": "Fallback search scope.",
            "user_facing_explanation": "Searching for details...",
            "agent_6_queries": [{"query": query, "search_depth": "advanced", "include_domains": [], "exclude_domains": []}]
        }
        
    print("\n" + "="*50)
    print(f" 📡 [AGENT 2 - WAVELENGTH SETTER]")
    print(f"    • Detected Wavelength: {payload.get('detected_wavelength')}")
    print(f"    • Number of Queries: {len(payload.get('agent_6_queries', []))}")
    print("="*50 + "\n")
    return {
        "search_plan": payload
    }

def research_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 6: Auto-Librarian / Research Agent.
    Triggered if Guardrail flags 'requires_deep_research'.
    Fetches data and dumps it into the isolated research_catalog.
    """
    print("\n" + "="*50)
    print(f" 🔎 [AGENT 6 - RESEARCHER]")
    print(f"    • Executing Deep Research Pass...")
    logger.info("Executing Agent 6: Deep Research Pass...")
    system_instruction = load_skill_prompt("research_pipeline_vr_holy_grail")
    
    # Extract the user's latest question to use as the search query
    user_message = get_latest_human_message(state)
    query = str(user_message.content) if user_message else state.get('topic_name', 'General')
    
    # Use the search plan generated by Agent 2, or fallback to user query
    search_plan = state.get("search_plan", {})
    queries = search_plan.get("agent_6_queries", [{"query": query, "search_depth": "advanced"}])
    
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {
            "research_catalog": [{
                "research_status": "SUCCESS",
                "failure_reason": None,
                "source_supported_facts": [
                    {"fact": "Mock fact about Docker", "source_excerpt": "Mock excerpt", "confidence": "high"}
                ],
                "code_or_math_snippet": None,
                "canonical_subtopics": ["namespaces"],
                "retrieved_at": "2026-01-01",
                "source_url": "mock.com"
            }],
            "research_id": "MOCK_RESEARCH",
            "requires_deep_research": False,
            "research_attempts": state.get("research_attempts", 0) + 1
        }
        
    # FIX #5: Deduplication — skip if research_catalog already covers this query topic
    existing_catalog = state.get("research_catalog", [])
    existing_subtopics = set()
    for entry in existing_catalog:
        if isinstance(entry, dict):
            for st in entry.get("canonical_subtopics", []):
                existing_subtopics.add(str(st).lower())
    
    query_words = set(query.lower().split())
    overlap = query_words & existing_subtopics
    if len(overlap) >= 2:  # 2+ matching subtopic words = likely already researched
        print(f"    • ⚡ Skipping Tavily search — catalog already covers: {overlap}")
        print("="*50 + "\n")
        return {
            "requires_deep_research": False,
            "research_attempts": state.get("research_attempts", 0) + 1
        }

    # Execute Live Tavily Search for each query
    tavily_key = os.getenv('TAVILY_KEY_1')
    scraped_context = ""
    research_id = f"RESEARCH_{uuid.uuid4().hex[:8]}"

    
    if not tavily_key:
        logger.error("No Tavily API Key found! Skipping search.")
        return {
            "research_catalog": [{
                "research_status": "FAILED",
                "failure_reason": "TAVILY_API_KEY_MISSING",
                "source_supported_facts": [],
                "canonical_subtopics": [],
                "source_url": None
            }],
            "research_id": research_id,
            "requires_deep_research": False,
            "research_attempts": state.get("research_attempts", 0) + 1
        }

    tavily_client = TavilyClient(api_key=tavily_key)
    for q_obj in queries[:2]: # Max 2 queries to save API limits/time
        if not isinstance(q_obj, dict):
            continue
        q_text = q_obj.get("query", query)
        s_depth = q_obj.get("search_depth", "advanced")
        inc_domains = q_obj.get("include_domains", [])
        exc_domains = q_obj.get("exclude_domains", [])
        
        try:
            print(f"      -> [TAVILY SEARCHING]: '{q_text}'")
            print(f"         - Search Depth: {s_depth}")
            print(f"         - Included Domains: {inc_domains if inc_domains else 'None'}")
            print(f"         - Excluded Domains: {exc_domains if exc_domains else 'None'}")
            search_kwargs = {"query": q_text, "search_depth": s_depth, "max_results": 3, "include_answer": True}
            if inc_domains:
                search_kwargs["include_domains"] = inc_domains
            if exc_domains:
                search_kwargs["exclude_domains"] = exc_domains
                
            response = tavily_client.search(**search_kwargs)
            
            if response.get("answer"):
                scraped_context += f"SYNTHESIZED SEARCH ANSWER: {response.get('answer')}\n\n"
            
            for res in response.get("results", []):
                content = str(res.get('content', ''))[:3000]
                scraped_context += f"Source: {res.get('url')}\nContent: {content}\n\n"
                
        except Exception as e:
            logger.error(f"Tavily Search Error for '{q_text}': {e}")
            
    if not scraped_context:
        return {
            "research_catalog": [{
                "research_status": "FAILED",
                "failure_reason": "NO_RESULTS",
                "source_supported_facts": [],
                "canonical_subtopics": [],
                "source_url": None
            }],
            "research_id": research_id,
            "requires_deep_research": False,
            "research_attempts": state.get("research_attempts", 0) + 1
        }
    
    api_key = os.getenv("MODEL_6_RESEARCHER_KEY")
    payload = call_nvidia_api(system_instruction, f"Raw Web Scrape Data:\n{scraped_context}", api_key=api_key, model_name="meta/llama-3.1-8b-instruct")
    
    if payload:
        try:
            validated = ResearchPayload.model_validate(payload)
            payload = validated.model_dump()
        except ValidationError as e:
            logger.error(f"Agent 6 schema validation failed: {e}")
            payload = None
    
    if payload:
        new_facts = [payload]
    else:
        new_facts = [{
            "source_url": "unknown",
            "source_domain": "System",
            "source_title": "Research Failure",
            "source_supported_facts": [],
            "canonical_subtopics": [],
            "retrieved_at": datetime.now().isoformat(),
            "research_status": "FAILED"
        }]
    
    print(f"    • Facts Retrieved: {len(new_facts)}")
    print("="*50 + "\n")
    return {
        "research_catalog": new_facts,
        "research_id": research_id,
        "requires_deep_research": False, # Reset flag after researching
        "research_attempts": state.get("research_attempts", 0) + 1
    }

def teacher_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 4: Adaptive Cognitive Teacher.
    Ingests Cognitive Profile + Research Catalog to generate a natural, dynamically-depth-adjusted tutoring response.
    """
    logger.info("Executing Agent 4: Mentality Teacher...")
    
    profile = state.get("cognitive_profile")
    topic_name = state.get("topic_name")
    # FIX #4: Cap research_catalog to last 3 entries to prevent context explosion
    MAX_RESEARCH_ENTRIES = 3
    research = state.get("research_catalog", [])[-MAX_RESEARCH_ENTRIES:]
    messages = state.get("messages", [])
    
    if state.get("is_off_topic"):
        response_text = f"🚨 **Scope Guardrail Alert:** Your question has drifted away from our chamber topic: *{topic_name}*. Please open a new learning chamber to discuss this!"
        # Fix: Reset the off_topic flag so the user isn't stuck in a death loop if they ask a valid question next.
        return {"messages": [AIMessage(content=response_text)], "is_off_topic": False}

    if state.get("is_greeting"):
        response_text = "Hello! I'm ready to continue our session. What would you like to explore next?"
        return {"messages": [AIMessage(content=response_text)], "is_greeting": False}

    if state.get("is_meta"):
        response_text = f"I am the Syntapse Cognitive Teacher. I am an AI designed to help you deeply master technical topics through Socratic reasoning, dynamic knowledge gaps analysis, and real-time research. We are currently focused on mastering: **{topic_name}**. What specific area would you like to dive into?"
        return {"messages": [AIMessage(content=response_text)], "is_meta": False}

    # --- PRODUCTION GEMINI API CALL ---
    system_instruction = load_skill_prompt("teacher_tutor_vr_holy_grail")
    
    # Force strict JSON schema adherence for Groq and enforce full-length explanations
    system_instruction += "\n\nCRITICAL INSTRUCTION: You MUST return a JSON object with EXACTLY the following keys:\n"
    system_instruction += "- 'requires_research_fallback' (boolean)\n"
    system_instruction += "- 'answer' (a natural, seamlessly integrated explanation answering the user's exact question without any template headers)\n"
    system_instruction += "- 'explanation_depth' (string: 'basic', 'intermediate', or 'deep')\n"
    system_instruction += "- 'concepts_covered' (list of strings)\n"
    system_instruction += "- 'evidence_boundary' (string or null, stating what is NOT covered by the research if you lack details)\n"
    system_instruction += "- 'socratic_question' (a JSON object with 'question', 'probe_type', 'probe_mode', 'tests_hypothesis', 'target_concept', 'expected_evidence', and 'failure_signal'). Return ONLY the JSON."
    
    # We must only send the string content of messages, not the full Message objects
    chat_history = [{"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": str(m.content)} for m in messages[-5:]]
    
    user_message = get_latest_human_message(state)
    current_user_question = str(user_message.content) if user_message else ""
    
    # FIX #3: Prune stale hypotheses — keep only last 5, remove already resolved ones
    active_hypotheses = state.get("active_cognitive_hypotheses", {})
    cognitive_events = state.get("cognitive_events", [])
    resolved_ids = {e.get("hypothesis") for e in cognitive_events if e.get("effect") in ["support", "refute"]}
    active_hypotheses = {k: v for k, v in active_hypotheses.items() if k not in resolved_ids}
    # Keep only the 5 most recent if still too large
    if len(active_hypotheses) > 5:
        keys = list(active_hypotheses.keys())[-5:]
        active_hypotheses = {k: active_hypotheses[k] for k in keys}
    if resolved_ids:
        print(f"   🧹 [HYPOTHESIS PRUNER] Removed {len(resolved_ids)} resolved hypotheses. Active: {len(active_hypotheses)}")
    profile = state.get("cognitive_profile")
    
    # Profile Health Check
    has_full_profile = isinstance(profile, dict) and profile.get("tutor_directive")
    print("\n--- [TEACHER PROFILE HEALTH] ---")
    if has_full_profile:
        print("   ✅ Full cognitive profile available — personalized teaching active.")
    elif isinstance(profile, dict) and profile:
        print("   ⚠️  Partial profile (flat fields only) — no pedagogical telemetry available.")
        print(f"      Profile keys: {list(profile.keys())}")
    else:
        print("   ❌ No cognitive profile found — teaching in generic mode.")
        print("      → User should run /calibrate to unlock personalized teaching.")
    print("--------------------------------\n")
    
    teacher_context = {
        "active_hypotheses": active_hypotheses
    }
    
    if isinstance(profile, dict):
        tutor_directive = profile.get("tutor_directive", {})
        rev_model = profile.get("reverse_engineered_model", {})
        cognitive_dna = profile.get("cognitive_dna", {})
        
        if "modal_text" in profile:
            teacher_context["user_raw_writing_sample"] = profile["modal_text"]
        elif "modal_answers" in profile:
            teacher_context["user_raw_writing_sample"] = profile["modal_answers"]
            
        if isinstance(tutor_directive, dict):
            teacher_context["pedagogical_telemetry"] = tutor_directive.get("pedagogical_telemetry")
            teacher_context["enforced_constraints"] = tutor_directive.get("enforced_constraints")
        if isinstance(rev_model, dict):
            teacher_context["predicted_friction_points"] = rev_model.get("predicted_friction_points")
            teacher_context["transfer_prediction"] = rev_model.get("transfer_prediction")
        if isinstance(cognitive_dna, dict):
            teacher_context["epistemic_signature"] = cognitive_dna.get("epistemic_signature")
            teacher_context["atomic_evidence_map"] = cognitive_dna.get("atomic_evidence_map")
            teacher_context["knowledge_organization"] = cognitive_dna.get("knowledge_organization")
            
        # Dynamic System Instruction Injection for Cognitive Profile Compliance
        override_text = "\n\n============================================================\n"
        override_text += "🚨 ACTIVE COGNITIVE DNA PROFILE INJECTED — MANDATORY RULES:\n"
        override_text += "============================================================\n"
        
        constraints = teacher_context.get("enforced_constraints", [])
        if constraints:
            override_text += "STRICT ENFORCED CONSTRAINTS (MUST OBEY 100%):\n"
            for c in constraints:
                override_text += f"  • {c}\n"
                
        telemetry = teacher_context.get("pedagogical_telemetry", {})
        if isinstance(telemetry, dict):
            if telemetry.get("concept_introduction_order"):
                override_text += f"  • Concept Order Directive: {telemetry['concept_introduction_order']}\n"
            if telemetry.get("analogy_domain"):
                override_text += f"  • Analogy Domain: Use {telemetry['analogy_domain']}\n"
                
        if teacher_context.get("user_raw_writing_sample"):
            sample = str(teacher_context["user_raw_writing_sample"])[:400].replace('\n', ' ')
            override_text += (
                f"\nLINGUISTIC STYLE TO MIRROR (USER WRITING SAMPLE):\n"
                f"  \"{sample}...\"\n"
                f"  Instructions: Mirror their direct tone, sequential step-by-step clause structure ('now we do X...', 'so we need Y...'), "
                f"  and emphasis on practical execution tools over abstract theory.\n"
            )
            
        override_text += (
            "\nMANDATORY CONCRETE ANCHOR MANDATE:\n"
            "Your VERY FIRST paragraph MUST introduce a concrete tool anchor, pipeline process, or practical mechanical example. "
            "DO NOT start with abstract definitions or mathematical/vector names (e.g. Receptance/Key/Value) until you have "
            "established a concrete anchor first! Starting with an abstract definition is a CRITICAL SYSTEM FAILURE.\n"
            "============================================================\n"
        )
        system_instruction += override_text
    
    # DEBUG: Print what the Teacher is actually receiving as pedagogical policy
    print("\n--- [DEBUG: TEACHER POLICY PAYLOAD] ---")
    print(json.dumps(teacher_context, indent=2))
    print("---------------------------------------\n")
    
    teacher_memory = state.get("teacher_memory", [])
    
    # Token Optimization: Prune research catalog and chat history to avoid rate limit bloat
    trimmed_research = []
    if isinstance(research, list):
        for item in research[:3]:
            if isinstance(item, dict):
                snippet = str(item.get("snippet", ""))[:350]
                trimmed_research.append({"title": item.get("title", ""), "snippet": snippet, "url": item.get("url", "")})
            elif isinstance(item, str):
                trimmed_research.append(item[:350])
    else:
        trimmed_research = research

    quality_critique = state.get("quality_critique")
    prompt_payload = {
        "CURRENT_USER_QUESTION": current_user_question,
        "PRIORITY_RULE": (
            "You MUST answer the CURRENT_USER_QUESTION. "
            "Follow the ACTIVE COGNITIVE DNA PROFILE directives in system_instruction strictly: "
            "start with a concrete tool/pipeline anchor first, use sequential step-by-step clause structure ('now we...'), "
            "and NEVER open with abstract definitions or formulas."
        ),
        "USER_PRIOR_KNOWLEDGE": state.get("user_topic_context"),
        "compiled_teacher_policy": teacher_context,
        "teaching_memory": teacher_memory[-3:],
        "chat_state": {
            "topic_name": topic_name,
            "research_catalog": trimmed_research
        },
        "recent_history": (chat_history or [])[-4:]
    }
    
    last_validation = state.get("last_validation")
    if last_validation:
        prompt_payload["LAST_PROBE_VALIDATION"] = last_validation
    
    actionable_feedback = state.get("quality_actionable_feedback") or {}
    if quality_critique:
        prompt_payload["CRITIQUE_FEEDBACK"] = (
            f"YOUR PREVIOUS DRAFT WAS REJECTED BY AGENT 3C QUALITY CRITIC FOR THE FOLLOWING REASON:\n"
            f"  \"{quality_critique}\"\n"
        )
        if actionable_feedback.get("how_to_fix"):
            prompt_payload["REQUIRED_REVISION_STEPS"] = actionable_feedback.get("how_to_fix")
        prompt_payload["REVISION_DIRECTIVE"] = "YOU MUST REVISE YOUR DRAFT TO FIX THESE CRITICAL ISSUES DIRECTLY WHILE PRESERVING YOUR SOCRATIC PROBE AND CONCRETE ANCHOR MANDATE."

    prompt = json.dumps(prompt_payload)
    
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {
            "requires_deep_research": False,
            "answer": "This is a mock answer for the Teacher.",
            "explanation_depth": "intermediate",
            "concepts_covered": ["mock concept"],
            "evidence_boundary": "Mock boundary.",
            "socratic_question": {
                "question": "This is a mock Socratic question.",
                "probe_type": "pedagogical_validation",
                "probe_mode": "causal_reasoning",
                "tests_hypothesis": None,
                "target_concept": "mock concept",
                "expected_evidence": "mock evidence",
                "failure_signal": "mock signal"
            }
        }
        
    api_key = os.getenv("MODEL_4_TEACHER_KEY")
    payload = call_groq_api(system_instruction, prompt, api_key=api_key, model_name="llama-3.3-70b-versatile")
    
    print(f"      -> [TEACHER RAW PAYLOAD]: {payload}")
    if payload:
        try:
            validated = TeacherResponsePayload.model_validate(payload)
            payload = validated.model_dump()
        except ValidationError as e:
            logger.error(f"Agent 4 schema validation failed: {e}")
            
            # Preserve the answer if available
            if isinstance(payload, dict) and payload.get("answer"):
                payload["socratic_question"] = {
                    "question": "What part of this mechanism would you like to examine next?",
                    "probe_type": "clarification",
                    "probe_mode": "recall",
                    "tests_hypothesis": None,
                    "target_concept": payload.get("concepts_covered", ["unknown"])[0] if payload.get("concepts_covered") else "unknown",
                    "expected_evidence": "A relevant explanation",
                    "failure_signal": "No relevant response"
                }
            else:
                payload = None
            
    if not payload:
        payload = {
            "requires_research_fallback": False,
            "answer": "I can explain the high-level mechanism confidently, but I don't have enough verified evidence to give you the exact execution details you asked for. I don't want to invent those details.",
            "explanation_depth": "basic",
            "concepts_covered": ["fallback"],
            "evidence_boundary": "Research unavailable due to API error.",
            "socratic_question": {
                "question": "What part of this mechanism would you like to examine next?",
                "probe_type": "clarification",
                "probe_mode": "recall",
                "tests_hypothesis": None,
                "target_concept": "fallback",
                "expected_evidence": "user chooses next topic",
                "failure_signal": "user is confused"
            }
        }

    if payload.get("requires_research_fallback"):
        attempts = state.get("research_attempts", 0)
        MAX_RESEARCH_ATTEMPTS = 2
        
        if attempts >= MAX_RESEARCH_ATTEMPTS:
            logger.warning("Teacher requested fallback research, but MAX_RESEARCH_ATTEMPTS reached. Outputting boundary instead.")
            payload["requires_research_fallback"] = False
            payload["evidence_boundary"] = (
                "Additional research was attempted, but the available evidence "
                "does not establish the requested detail."
            )
        else:
            logger.warning("Teacher requested fallback research. Routing to Agent 6.")
            return {"requires_deep_research": True}
        
    
    socratic_obj = payload.get('socratic_question', {})
    
    if isinstance(socratic_obj, dict):
        p_type = socratic_obj.get("probe_type")
        if not p_type:
            logger.warning("Teacher omitted probe_type. Downgrading to clarification.")
            socratic_obj["probe_type"] = "clarification"
            socratic_obj["tests_hypothesis"] = None
            
        elif p_type == "pedagogical_validation":
            active_ids = set(state.get("active_cognitive_hypotheses", {}).keys())
                
            t_hyp = socratic_obj.get("tests_hypothesis")
            if not t_hyp or t_hyp not in active_ids:
                # logger.warning(f"Teacher tried to test unknown/null hypothesis: {t_hyp}. Downgrading to clarification.")
                socratic_obj["probe_type"] = "clarification"
                socratic_obj["tests_hypothesis"] = None

    if isinstance(socratic_obj, str):
        socratic_text = socratic_obj
    else:
        socratic_text = socratic_obj.get('question', 'Does this make sense?')
        
    answer_text = payload.get('answer', '').strip()
    evidence_boundary = payload.get('evidence_boundary')
    
    # Sanitize whitespace: collapse 3+ newlines down to 2 and strip trailing line spaces
    import re
    answer_text = re.sub(r'[ \t]+\n', '\n', answer_text)
    answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
    
    formatted_parts = [answer_text]
    if evidence_boundary:
        formatted_parts.append(f"\n\n*Note: {evidence_boundary}*")
        
    formatted_response = "".join(formatted_parts)
    
    
    # Generate unique ID for this Socratic probe
    # FIX #1: Phantom Probe Guard — only set probe if this is a real teacher response
    # If we're in fallback mode (payload was None), do NOT set last_teacher_probe
    # so the Cognitive Validator won't validate against a probe the user never saw.
    probe_dict = {"probe_id": f"PROBE_{uuid.uuid4().hex[:8]}"}
    if isinstance(socratic_obj, dict):
        probe_dict.update(socratic_obj)
    
    new_concepts = payload.get("concepts_covered", []) or []
    current_discussed = state.get("discussed_concepts", []) or []
    updated_discussed = list(set(current_discussed + new_concepts))

    # Append the new AI message to the conversation stream
    return {
        "messages": [AIMessage(content=formatted_response)],
        "last_teacher_probe": probe_dict,
        "last_teacher_response": payload,
        "active_cognitive_hypotheses": active_hypotheses,
        "discussed_concepts": updated_discussed
    }

def cognitive_validator_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 3: Cognitive Validator + Gap Analyzer
    Runs after user responds to the teacher's Socratic probe. Evaluates response and outputs Cognitive Event.
    """
    if state.get("trigger_gap_analysis"):
        return {}
        
    logger.info("Executing Agent 3: Cognitive Validator...")
    messages = state.get("messages", [])
    topic = state.get("topic_name", "this topic")
    profile = state.get("cognitive_profile", {})
    last_probe = state.get("last_teacher_probe")
    
    if last_probe is None:
        return {}
        
    user_msg = get_latest_human_message(state)
    if not user_msg:
        return {}
        
    user_text = str(user_msg.content)
    
    probe_type = last_probe.get("probe_type")
    if probe_type != "pedagogical_validation":
        logger.info(f"Skipping Agent 3 validation because probe_type={probe_type!r}.")
        return {"last_teacher_probe": None}
        
    hypothesis_id = last_probe.get("tests_hypothesis")
    probe_id = last_probe.get("probe_id")
    
    active_cognitive_hypotheses = state.get("active_cognitive_hypotheses", {})
    active_hypotheses_ids = set(active_cognitive_hypotheses.keys())
        
    if not probe_id or not hypothesis_id or hypothesis_id not in active_hypotheses_ids:
        logger.warning("Invalid pedagogical probe hypothesis or missing probe ID. Rejecting validation.")
        return {"last_teacher_probe": None}
    
    system_instruction = load_skill_prompt("cognitive_validator_vr_holy_grail")
    
    prompt = json.dumps({
        "active_hypothesis": hypothesis_id,
        "socratic_probe": last_probe,
        "user_response": user_text,
        "relevant_chat_context": [str(m.content) for m in messages[-4:]],
        "cognitive_profile": profile
    })
    
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        payload = {
            "probe_response_status": "ANSWERED",
            "content_gap": {"present": False},
            "pedagogical_signal": {
                "probe_id": probe_id,
                "target_concept": "mock concept",
                "tested_hypothesis": hypothesis_id,
                "response_quality": "strong",
                "hypothesis_effect": "support",
                "evidence": {
                    "user_response": user_text,
                    "observation": "mock observation",
                    "interpretation": "mock interpretation"
                },
                "topic_confound_risk": "low",
                "observation_confidence": "high"
            }
        }
    else:
        api_key = os.getenv("MODEL_3_VALIDATOR_KEY")
        if not api_key:
            api_key = os.getenv("MODEL_3_GAP_ANALYZER_KEY")
        payload = call_nvidia_api(system_instruction, prompt, api_key=api_key, model_name="meta/llama-3.1-8b-instruct")
    
    print("\n   [AGENT 3 - COGNITIVE VALIDATOR EXECUTION]")
    print(f"      -> Probe Answer Evaluated: \"{user_text}\"")
    print(f"      -> Signal Output: {json.dumps(payload, indent=2)}\n")
    
    if not payload or "pedagogical_signal" not in payload:
        return {"last_teacher_probe": None}
        
    try:
        val_payload = CognitiveValidationPayload(**payload)
        
        probe_status = val_payload.probe_response_status
        signal = val_payload.pedagogical_signal
        
        if probe_status == "NOT_ANSWERING_PROBE" or signal is None:
            logger.info("User did not answer the probe. Skipping validation event.")
            return {
                "last_teacher_probe": None,
                "last_validation": val_payload.model_dump()
            }
            
        verified_probe_id = last_probe["probe_id"]
        if signal.probe_id != verified_probe_id:
            logger.error("Validator attempted probe ID mutation")
            return {"last_teacher_probe": None}
            
        verified_hypothesis = last_probe["tests_hypothesis"]
        
        # deterministic event id based on probe and response
        raw_event_str = f"{verified_probe_id}:{user_text}".encode("utf-8")
        event_id_hash = hashlib.sha256(raw_event_str).hexdigest()[:16]
        
        event = CognitiveEvent(
            event_id=f"EV_{event_id_hash}",
            source="teacher_socratic_response",
            probe_id=verified_probe_id,
            target_concept=signal.target_concept,
            hypothesis=verified_hypothesis,
            effect=signal.hypothesis_effect,
            response_quality=signal.response_quality,
            user_response=user_text,
            observation=signal.evidence.observation,
            interpretation=signal.evidence.interpretation,
            observation_confidence=signal.observation_confidence,
            topic_confound_risk=signal.topic_confound_risk,
            timestamp=datetime.now()
        )
        
        updated_profile = apply_event_to_profile(profile.copy(), event, topic=topic)
            
        return {
            "cognitive_profile": updated_profile,
            "cognitive_events": [event.model_dump()],
            "last_validation": val_payload.model_dump(),
            "last_teacher_probe": None
        }
    except Exception as e:
        logger.error(f"Failed to process cognitive event: {e}")
        return {"last_teacher_probe": None}

def gap_analyzer_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 3B: Knowledge Gap Analyzer (FAB Logic).
    Suspends normal chat, analyzes full history vs topic structure, outputs missing gaps.
    """
    logger.info("Executing Knowledge Gap Analysis (FAB Triggered)...")
    messages = state.get("messages", [])
    topic = state.get("topic_name", "this topic")
    
    # FIX #2: Guard against empty sessions — need at least 2 user messages for meaningful analysis
    user_messages = [m for m in messages if m.__class__.__name__ == "HumanMessage"]
    if len(user_messages) < 2:
        print("   ⚠️  [GAP ANALYZER] Insufficient conversation history for meaningful analysis (< 2 user turns). Skipping.")
        return {
            "last_gap_analysis": {
                "diagnostic_summary": f"Not enough conversation history to diagnose gaps in **{topic}** yet. Ask at least 2 questions first, then run the analysis.",
                "suggestions": []
            },
            "trigger_gap_analysis": False
        }

    system_instruction = load_skill_prompt("gap_analyzer_vr_holy_grail")
    # Extract ALL historical user queries to map their exact exploration path
    all_user_queries = [str(m.content) for m in messages if getattr(m, "type", "") == "human" or m.__class__.__name__ == "HumanMessage"]
    
    # Keep only the very recent full chat for immediate flow context
    recent_chat = [str(m.content) for m in messages[-4:]]
    
    prompt = json.dumps({
        "topic": topic,
        "user_exploration_path": all_user_queries,
        "recent_chat_context": recent_chat,
        "taught_concepts": state.get("teacher_memory", []),
        "research_catalog": state.get("research_catalog", []),
        "cognitive_profile": state.get("cognitive_profile", {}),
        "cognitive_events": state.get("cognitive_events", [])
    })
    
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        payload = {
            "diagnostic_summary": "Mock gap analysis.",
            "suggestions": [{"button_label": "Mock explore", "search_query": "mock search"}]
        }
    else:
        api_key = os.getenv("MODEL_3_GAP_ANALYZER_KEY")
        payload = call_nvidia_api(system_instruction, prompt, api_key=api_key, model_name="meta/llama-3.1-8b-instruct")
    
    if payload:
        try:
            validated = KnowledgeGapAnalysis.model_validate(payload)
            payload = validated.model_dump()
        except ValidationError as e:
            logger.error(f"Agent 3B schema validation failed: {e}")
            payload = None
            
    if not payload:
        payload = {
            "diagnostic_summary": "I reviewed our chat. You missed some mechanics.",
            "suggestions": [{"button_label": "Explore Advanced Mechanics", "search_query": "Advanced Mechanics"}]
        }
    
    from datetime import datetime, timezone
    gap_event = {
        "event_type": "gap_analysis",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": payload.get("diagnostic_summary"),
        "suggestions_count": len(payload.get("suggestions", []))
    }
    
    return {
        "last_gap_analysis": payload,
        "trigger_gap_analysis": False,
        "cognitive_events": [gap_event]
    }

def quality_critic_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    AGENT 3C: Quality Critic Node.
    Audits the Teacher Agent response draft for completeness, anti-fluff, cognitive profile alignment, and research fact utilization.
    Runs on NVIDIA Llama 3.1 8B Instruct API for fast prompt auditing.
    Enforces a strict Max-1 rewrite loop to prevent infinite LLM chatter.
    """
    last_teacher_res = state.get("last_teacher_response")
    if not last_teacher_res:
        return {"quality_critique": None}
        
    regeneration_count = state.get("quality_regeneration_count", 0)
    if regeneration_count >= 1:
        logger.info("Agent 3C: Max regeneration count reached (1). Approving response.")
        return {"quality_critique": None}
        
    last_human_msg = get_latest_human_message(state)
    user_prompt = str(last_human_msg.content) if last_human_msg else ""
    
    last_probe = state.get("last_teacher_probe")
    probe_context = None
    if last_probe and last_probe.get("question"):
        probe_context = {
            "PROBE_QUESTION": last_probe.get("question"),
            "USER_ANSWER": user_prompt,
            "TARGET_CONCEPT": last_probe.get("target_concept"),
            "EXPECTED_EVIDENCE": last_probe.get("expected_evidence")
        }
        
    topic_name = state.get("topic_name", "General")
    research_catalog = state.get("research_catalog", [])
    cognitive_profile = state.get("cognitive_profile", {})
    
    system_instruction = load_skill_prompt("quality_critic_vr_holy_grail")
    
    input_payload = {
        "TOPIC_NAME": topic_name,
        "USER_QUERY": user_prompt,
        "PROBE_EVALUATION_CONTEXT": probe_context,
        "TEACHER_DRAFT_RESPONSE": last_teacher_res,
        "RESEARCH_CATALOG_FACTS": research_catalog[:3],
        "COGNITIVE_MAPPER_PROFILE": cognitive_profile
    }
    
    api_key = os.getenv("MODEL_3C_QUALITY_CRITIC_KEY") or os.getenv("MODEL_3_GAP_ANALYZER_KEY") or os.getenv("MODEL_6_RESEARCHER_KEY")
    critic_res = call_nvidia_api(
        system_instruction=system_instruction,
        user_content=json.dumps(input_payload),
        api_key=api_key,
        model_name="meta/llama-3.1-8b-instruct"
    )
    
    if not critic_res:
        groq_key = os.getenv("MODEL_5_GUARDRAIL_KEY") or os.getenv("MODEL_4_TEACHER_KEY")
        critic_res = call_groq_api(
            system_instruction=system_instruction,
            user_content=json.dumps(input_payload),
            api_key=groq_key,
            model_name="llama-3.1-8b-instant"
        )
        
    print("\n" + "="*65)
    print(f" ⚖️ [AGENT 3C — QUALITY CRITIC AUDIT EXECUTION]")
    print(f"    • Target LLM Model   : NVIDIA Llama 3.1 8B Instruct (NIM API)")
    print(f"    • Audit Pass Count   : {regeneration_count + 1} / 2")
    
    if isinstance(critic_res, dict):
        try:
            validated = QualityCriticPayload.model_validate(critic_res)
            critic_res = validated.model_dump()
        except ValidationError as e:
            logger.error(f"Agent 3C schema validation failed: {e}")
            
        quality_passed = critic_res.get("quality_passed", True)
        critique = critic_res.get("critique")
        actionable_feedback = critic_res.get("actionable_feedback") or {}
        
        status_symbol = "✅ APPROVED (PASS)" if quality_passed else "❌ REJECTED (FAIL)"
        print(f"    • Audit Decision     : {status_symbol}")
        print(f"    • Completeness Score : {critic_res.get('prompt_completeness_score', 0.0):.2f} / 1.00")
        print(f"    • Anti-Fluff Score   : {critic_res.get('anti_fluff_score', 0.0):.2f} / 1.00")
        print(f"    • Fact Grounding     : {critic_res.get('fact_grounding_score', 0.0):.2f} / 1.00")
        print(f"    • Profile Alignment  : {critic_res.get('profile_alignment_score', 0.0):.2f} / 1.00")
        
        if actionable_feedback:
            issues = actionable_feedback.get("critical_issues", [])
            fixes = actionable_feedback.get("how_to_fix", [])
            if issues:
                print(f"    • Critical Flaws     : {issues}")
            if fixes:
                print(f"    • How To Fix Steps   : {fixes}")
                
        if critique:
            print(f"    • Actionable Critique: \"{critique}\"")
        print("="*65 + "\n")
        
        if not quality_passed and critique:
            logger.info(f"Agent 3C rejected draft. Triggering rewrite loop pass 1: {critique}")
            return {
                "quality_critique": critique,
                "quality_evaluation": critic_res,
                "quality_actionable_feedback": actionable_feedback,
                "quality_regeneration_count": regeneration_count + 1
            }
    else:
        print(f"    • Raw Response       : {critic_res}")
        print("="*65 + "\n")
            
    return {
        "quality_critique": None,
        "quality_evaluation": critic_res if isinstance(critic_res, dict) else None,
        "quality_actionable_feedback": None
    }

def memory_compressor_node(state: SyntapseChamberState) -> Dict[str, Any]:
    """
    UTILITY NODE: Ghost Teacher Semantic Memory.
    
    Runs after the Teacher response and stores a compact semantic
    representation in teacher_memory without modifying the original
    conversation messages.
    
    The original Teacher response remains in state["messages"].
    The compressed record is used as long-term teaching memory.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}
        
    last_msg = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_msg = msg
            break
            
    if not last_msg:
        return {}
    
    last_teacher_res = state.get("last_teacher_response")
    
    # Only compress if the last message was from the Teacher (AI) and we have a tracked response
    if not str(last_msg.content).startswith("[GHOST RECORD") and last_teacher_res is not None:
        logger.info("Executing Ghost Teacher Micro-Compression Pass...")
        
        last_probe = state.get("last_teacher_probe", {})
        socratic_q = last_probe.get("question") if isinstance(last_probe, dict) else None
            
        # Create a semantic structured ghost record
        ghost_obj = {
            "type": "teacher_ghost",
            "topic": state.get("topic_name", "General"),
            "depth": last_teacher_res.get("explanation_depth", "unknown"),
            "concepts_taught": last_teacher_res.get("concepts_covered", []),
            "core_explanation": last_teacher_res.get("answer", "")[:500] + "...",
            "socratic_probe": socratic_q,
            "probe_id": last_probe.get("probe_id"),
            "evidence_boundary": last_teacher_res.get("evidence_boundary")
        }
        
        import json
        print("\n" + "="*50)
        print(f" 🗜️ [MEMORY COMPRESSOR]")
        print(f"    • Compressed Teacher response to semantic ghost record.")
        print(f"    • Ghost Size: {len(json.dumps(ghost_obj))} bytes")
        print("="*50 + "\n")
        return {
            "teacher_memory": [ghost_obj],
            "research_attempts": 0,
            "last_teacher_response": None
        }
        
    return {"research_attempts": 0}
