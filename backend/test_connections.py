import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load keys
load_dotenv()

def test_gemini(key: str, name: str, model_name: str):
    if not key:
        return "[FAILED] Skipped (No Key)"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
    data = json.dumps({"contents": [{"parts": [{"text": "Reply with OK"}]}]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "[SUCCESS] SUCCESS (Processing Active)"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return f"[FAILED] FAILED (HTTP {e.code}: {error_body[:100]}...)"
    except Exception as e:
        return f"[FAILED] FAILED ({str(e)})"

def test_groq(key: str, name: str, model_name: str):
    if not key:
        return "[FAILED] Skipped (No Key)"
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = json.dumps({"model": model_name, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "[SUCCESS] SUCCESS (Processing Active)"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return f"[FAILED] FAILED (HTTP {e.code}: {error_body[:100]}...)"
    except Exception as e:
        return f"[FAILED] FAILED ({str(e)})"

def test_nvidia(key: str, name: str, model_name: str):
    if not key:
        return "[FAILED] Skipped (No Key)"
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    data = json.dumps({"model": model_name, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "[SUCCESS] SUCCESS (Processing Active)"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return f"[FAILED] FAILED (HTTP {e.code}: {error_body[:100]}...)"
    except Exception as e:
        return f"[FAILED] FAILED ({str(e)})"

def test_tavily(key: str, index: int):
    if not key:
        return "[FAILED] Skipped (No Key)"
    url = "https://api.tavily.com/search"
    data = json.dumps({"api_key": key, "query": "test", "search_depth": "basic"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "[SUCCESS] SUCCESS (Processing Active)"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return f"[FAILED] FAILED (HTTP {e.code}: {error_body[:100]}...)"
    except Exception as e:
        return f"[FAILED] FAILED ({str(e)})"

def run_connection_tests():
    print("\n--- SYNTAPSE LIVE NETWORK & PROCESSING TEST ---")
    print("Sending live pings to Google, Groq, NVIDIA, and Tavily...\n")
    
    # 1. Test Mapper (Groq)
    m1 = "openai/gpt-oss-120b"
    print(f"Agent 1 (Mapper - Groq [{m1}]):        ", test_groq(os.getenv("MODEL_1_MAPPER_KEY"), "Mapper", m1))
    
    # 2. Test Wavelength (Groq)
    m2 = "openai/gpt-oss-120b"
    print(f"Agent 2 (Wavelength - Groq [{m2}]):    ", test_groq(os.getenv("MODEL_2_WAVELENGTH_KEY"), "Wavelength", m2))
    
    # 3. Test Gap Analyzer (Groq)
    m3 = "openai/gpt-oss-120b"
    print(f"Agent 3 (Gap Analyz - Groq [{m3}]):    ", test_groq(os.getenv("MODEL_3_GAP_ANALYZER_KEY"), "GapAnalyzer", m3))
    
    # 3C. Test Quality Critic (Groq)
    m3c = "openai/gpt-oss-120b"
    print(f"Agent 3C (Critic - Groq [{m3c}]):       ", test_groq(os.getenv("MODEL_3C_QUALITY_CRITIC_KEY"), "QualityCritic", m3c))
    
    # 4. Test Teacher (Groq)
    m4 = "openai/gpt-oss-120b"
    print(f"Agent 4 (Teacher - Groq [{m4}]):       ", test_groq(os.getenv("MODEL_4_TEACHER_KEY"), "Teacher", m4))
    
    # 5. Test Guardrail (Groq)
    m5 = "openai/gpt-oss-120b"
    print(f"Agent 5 (Guardrail - Groq [{m5}]):     ", test_groq(os.getenv("MODEL_5_GUARDRAIL_KEY"), "Guardrail", m5))
    
    # 6. Test Researcher (Groq)
    m6 = "openai/gpt-oss-120b"
    print(f"Agent 6 (Researcher - Groq [{m6}]):    ", test_groq(os.getenv("MODEL_6_RESEARCHER_KEY") or os.getenv("MODEL_4_TEACHER_KEY"), "Researcher", m6))
    
    fallback_key = os.getenv("NVIDIA_API_KEY")
    fallback_model = os.getenv("NVIDIA_MODEL_NAME", "nvidia/nemotron-3.5-lightning-30b-a3b")
    print(f"Fallback (NVIDIA [{fallback_model}]):", test_nvidia(fallback_key, "NVIDIA Fallback", fallback_model))
    
    print("\n--- Testing Tavily Round-Robin Keys ---")
    for i in range(1, 4):
        key = os.getenv(f"TAVILY_KEY_{i}")
        result = test_tavily(key, i)
        print(f"Tavily Key {i}: {result}")
        
    print("\n-------------------------------------------------\n")

if __name__ == "__main__":
    run_connection_tests()