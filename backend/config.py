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
# LLM MODEL HIERARCHY & LOAD BALANCING
# =====================================================================
# Distributing API keys and Model weights to prevent token rate-limiting
# and optimize latency/cost.
# Heavy Load -> Groq Llama 3.3 70B
# Medium Load -> Groq Llama 3.3 70B
# Fast/Light Load -> NVIDIA NIM (Llama 3.1 8B Instruct)
# =====================================================================

# --- AGENT 1: COGNITIVE MAPPER (HEAVY LOAD) ---
# Purpose: Deep psychometric analysis
MODEL_1_MAPPER_NAME = "llama-3.3-70b-versatile" # Groq Network
MODEL_1_MAPPER_KEY = os.getenv("MODEL_1_MAPPER_KEY")

# --- AGENT 2: WAVELENGTH SETTER (MID LOAD) ---
# Purpose: Fast JSON API configurations
MODEL_2_WAVELENGTH_NAME = "llama-3.3-70b-versatile" # Groq Network
MODEL_2_WAVELENGTH_KEY = os.getenv("MODEL_2_WAVELENGTH_KEY")

# --- AGENT 3: GAP ANALYZER (LIGHTWEIGHT) ---
# Purpose: FAB Logic and History diffing
MODEL_3_GAP_ANALYZER_NAME = "meta/llama-3.1-8b-instruct" # NVIDIA NIM Network
MODEL_3_GAP_ANALYZER_KEY = os.getenv("MODEL_3_GAP_ANALYZER_KEY")

# --- AGENT 4: TEACHER / TUTOR (MID LOAD) ---
# Purpose: Pedagogical synthesis and context management
MODEL_4_TEACHER_NAME = "llama-3.3-70b-versatile" # Groq Network
MODEL_4_TEACHER_KEY = os.getenv("MODEL_4_TEACHER_KEY")

# --- AGENT 5: GUARDRAIL (LIGHTWEIGHT) ---
# Purpose: Pre-flight security check on every user message
MODEL_5_GUARDRAIL_NAME = "llama-3.3-70b-versatile" # Groq Network
MODEL_5_GUARDRAIL_KEY = os.getenv("MODEL_5_GUARDRAIL_KEY")

# --- AGENT 6: AUTO-LIBRARIAN (LIGHTWEIGHT) ---
# Purpose: Extracting JSON facts from Tavily HTML scrapes
MODEL_6_RESEARCHER_NAME = "meta/llama-3.1-8b-instruct"
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

