"""
===============================================================================
 SYNAPSE BACKEND — Calibration Orchestrator (orchestrator.py)
===============================================================================
 Purpose:
   • Manages Agent 1 (Mapper) onboarding calibration execution outside the active
     chat graph to extract the baseline Cognitive Profile.

 Core Logic & Hierarchy:
   ├── live_agent_1_mapper : Accepts user writing essay sample
   ├── Skill Prompt Load   : Loads Agent 1 master directives from prompt_skills/
   ├── Epistemic Extraction: Calls Groq API to extract reasoning style & friction points
   └── Persist Footprint   : Saves baseline cognitive_profile.json to disk & state
===============================================================================
"""

import os
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_SKILLS_DIR = BASE_DIR / "prompt_skills"

def load_skill_prompt(skill_name: str) -> str:
    """Helper to load the markdown master directives reliably across working directories."""
    file_path = PROMPT_SKILLS_DIR / f"{skill_name}.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"System Prompt for {skill_name} not found."

def live_agent_1_mapper(modal_text: str) -> dict:
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {
            "cognitive_mechanics": {
                "input_quality": {"clarity": "high", "specificity": "high"},
                "syntax_of_thought": {"reasoning_style": "deductive"},
                "epistemic_signature": {"complexity_approach": "bottom-up"}
            },
            "grounded_profile": {
                "topic": "Docker",
                "friction_map": [],
                "depth_overlay": {"peaks_mapped": [], "valleys_mapped": []},
                "prerequisite_gaps": []
            },
            "tutor_directive": {
                "pedagogical_guidance": "Teach using real-world mechanics.",
                "intervention_triggers": []
            }
        }
        
    key = os.getenv("MODEL_1_MAPPER_KEY")
    if not key:
        return {"tutor_directive": "Follow user cues", "cognitive_mechanics": "Standard"}
        
    system_instruction = load_skill_prompt("cognitive_mapper_vr_holy_grail")
    
    # Force strict JSON schema adherence for Groq
    system_instruction += "\n\nCRITICAL INSTRUCTION: You MUST return a JSON object with EXACTLY the following top-level keys: 'cognitive_dna', 'reverse_engineered_model', and 'tutor_directive'. Do not include a 'technical_critique' or 'analysis' wrapper. Return ONLY the JSON."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"User Text to Analyze:\n{modal_text}"}
        ],
        "response_format": {"type": "json_object"}
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['choices'][0]['message']['content']
            # Clean markdown JSON block if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
    except Exception as e:
        print(f"      -> [API ERROR]: {e}")
        return {"tutor_directive": "Follow user cues", "cognitive_mechanics": "Standard"}

def live_agent_2_query_creator(topic: str) -> dict:
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return {"queries": [{"query": f"Advanced internals of {topic}", "search_depth": "advanced"}]}
        
    key = os.getenv("MODEL_2_WAVELENGTH_KEY")
    if not key:
        return {"queries": [f"What is {topic}"]}
        
    system_instruction = load_skill_prompt("wavelength_setter_vr_holy_grail")
    tavily_manual = load_skill_prompt("tavily_api_mini_manual")
    
    prompt = (
        f"TARGET TOPIC: '{topic}'\n"
        "Generate your ScopeSizerPayload in JSON format. "
        "CRITICAL: At least one query MUST be 'one level higher' (broader) to retrieve foundational structural context needed for building an Analogy Bridge. "
    )
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = json.dumps({
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": f"{system_instruction}\n\nTAVILY API MANUAL:\n{tavily_manual}"},
            {"role": "user", "content": prompt}
        ], 
        "response_format": {"type": "json_object"}
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['choices'][0]['message']['content']
            return json.loads(text)
    except Exception as e:
        print(f"      -> [API ERROR]: {e}")
        return {"queries": [f"What is {topic}"]}

def run_pre_chamber_agents(modal_answers: str, target_topic: str):
    print("\n" + "="*80)
    print("🚀 PHASE 0: PRE-CHAMBER INITIALIZATION (Live API Calls for Agents 1 & 2)")
    print("="*80)
    
    print("\n   [AGENT 1 TRIGGERED]: COGNITIVE MAPPER (Groq Llama-3.3 70B)")
    print(f"      -> Analyzing Modal: '{modal_answers}'")
    t0 = time.time()
    cognitive_profile = live_agent_1_mapper(modal_answers)
    elapsed = time.time() - t0
    print(f"      -> Linguistic Mechanics Extracted (No MBTI buckets):\n{json.dumps(cognitive_profile, indent=2)}\n      (Took {elapsed:.2f}s)")
    
    # 2. Agent 2 Query Creation (For the NEW topic they want to learn)
    print("\n   [AGENT 2 TRIGGERED]: QUERY CREATOR (Groq Llama-3.1)")
    t0 = time.time()
    search_queries = live_agent_2_query_creator(target_topic)
    elapsed = time.time() - t0
    print(f"      -> Search Queries Generated:\n{json.dumps(search_queries, indent=2)}\n      (Took {elapsed:.2f}s)")
    
    return cognitive_profile
