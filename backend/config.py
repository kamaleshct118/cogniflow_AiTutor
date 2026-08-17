"""
===============================================================================
 SYNAPSE BACKEND — Environment Configuration & API Keys (config.py)
===============================================================================
 Purpose:
   • Loads environment variables, manages Round-Robin rotation for Tavily search keys,
     and defines per-agent model configurations across Groq and NVIDIA NIM.

 Core Logic & Hierarchy:
   ├── Tavily Key Rotation  : get_next_tavily_key() (Round-robin sequence to avoid 429s)
   ├── Model Assignments    : MODEL_1 to MODEL_6 API keys & model endpoints
   └── Diagnostics Helper   : print_model_diagnostics() clean logger utility
===============================================================================
"""

import os
import itertools
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("syntapse.config")

# =====================================================================
# TAVILY API ROUND-ROBIN
# =====================================================================
TAVILY_KEYS = [
    os.getenv("TAVILY_KEY_1"),
    os.getenv("TAVILY_KEY_2"),
    os.getenv("TAVILY_KEY_3")
]
# Filter out any None values in case a key is missing
TAVILY_KEYS = [k for k in TAVILY_KEYS if k]
tavily_key_cycle = itertools.cycle(TAVILY_KEYS)

def get_next_tavily_key():
    """Returns the next Tavily API key in the Round-Robin sequence to prevent rate limits."""
    key = next(tavily_key_cycle)
    logger.info(f"🔄 Rotating Tavily API Key: {key[:12]}***")
    return key

# =====================================================================
# LLM MODEL HIERARCHY & DIRECT FALLBACK ARCHITECTURE
# =====================================================================
# Primary LLM Endpoint  : Groq Network ("openai/gpt-oss-120b")
# Direct Fallback Endpoint: NVIDIA NIM ("nvidia/nemotron-3.5-lightning-30b-a3b")
# =====================================================================

# --- AGENT 1: COGNITIVE MAPPER ---
# MODEL_1_MAPPER_NAME = "llama-3.3-70b-versatile"
MODEL_1_MAPPER_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_1_MAPPER_KEY = os.getenv("MODEL_1_MAPPER_KEY")

# --- AGENT 2: WAVELENGTH SETTER ---
# MODEL_2_WAVELENGTH_NAME = "llama-3.3-70b-versatile"
MODEL_2_WAVELENGTH_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_2_WAVELENGTH_KEY = os.getenv("MODEL_2_WAVELENGTH_KEY")

# --- AGENT 3: GAP ANALYZER ---
MODEL_3_GAP_ANALYZER_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_3_GAP_ANALYZER_KEY = os.getenv("MODEL_3_GAP_ANALYZER_KEY")

# --- AGENT 3C: QUALITY CRITIC ---
MODEL_3C_QUALITY_CRITIC_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_3C_QUALITY_CRITIC_KEY = os.getenv("MODEL_3C_QUALITY_CRITIC_KEY")

# --- AGENT 4: TEACHER / TUTOR ---
# MODEL_4_TEACHER_NAME = "llama-3.3-70b-versatile"
MODEL_4_TEACHER_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_4_TEACHER_KEY = os.getenv("MODEL_4_TEACHER_KEY")

# --- AGENT 5: GUARDRAIL ---
# MODEL_5_GUARDRAIL_NAME = "llama-3.3-70b-versatile"
MODEL_5_GUARDRAIL_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_5_GUARDRAIL_KEY = os.getenv("MODEL_5_GUARDRAIL_KEY")

# --- AGENT 6: AUTO-LIBRARIAN ---
# MODEL_6_RESEARCHER_NAME = "llama-3.3-70b-versatile"
MODEL_6_RESEARCHER_NAME = "openai/gpt-oss-120b" # Groq Network
MODEL_6_RESEARCHER_KEY = os.getenv("MODEL_6_RESEARCHER_KEY")

# =====================================================================
# DIAGNOSTICS
# =====================================================================
def print_model_diagnostics(agent_id: str, model_name: str, error_msg: str = None):
    """Utility to print specific API failures cleanly without confusing logs."""
    if error_msg:
        print(f"❌ [API FAILURE] {agent_id} failed using {model_name}. Error: {error_msg}")
    else:
        print(f"✅ [SUCCESS] {agent_id} executed securely via {model_name}.")

# =====================================================================
# SELF-TESTING BLOCK
# =====================================================================

