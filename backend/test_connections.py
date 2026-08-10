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
        with urllib.request.urlopen(req) as response:
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
    # Note: Added User-Agent to bypass Cloudflare 1010 block
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
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
    # Note: NVIDIA NIM URL endpoint structure
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    # data = json.dumps({"model": "meta/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}).encode('utf-8')
    data = json.dumps({"model": model_name, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
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
        with urllib.request.urlopen(req) as response:
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
    
    # 1. Test Mapper (Now uses Groq)
    print("Agent 1 (Mapper - Groq):     ", test_groq(os.getenv("MODEL_1_MAPPER_KEY"), "Mapper", "llama-3.3-70b-versatile"))
    
    # 2. Test Wavelength (Groq)
    print("Agent 2 (Wavelength - Groq): ", test_groq(os.getenv("MODEL_2_WAVELENGTH_KEY"), "Wavelength", "llama-3.3-70b-versatile"))
    
    # 3. Test Gap Analyzer (NVIDIA Llama 3.1)
    print("Agent 3 (Gap Analyz - NVIDIA):", test_nvidia(os.getenv("MODEL_3_GAP_ANALYZER_KEY"), "GapAnalyzer", "meta/llama-3.1-8b-instruct"))
    
    # 4. Test Teacher (Groq Llama 3.3)
    print("Agent 4 (Teacher - Groq):    ", test_groq(os.getenv("MODEL_4_TEACHER_KEY"), "Teacher", "llama-3.3-70b-versatile"))
    
    # 5. Test Guardrail (Groq Llama 3.3)
    print("Agent 5 (Guardrail - Groq):  ", test_groq(os.getenv("MODEL_5_GUARDRAIL_KEY"), "Guardrail", "llama-3.3-70b-versatile"))
    
    # 6. Test Researcher (NVIDIA Llama 3.1)
    print("Agent 6 (Researcher - NVIDIA):", test_nvidia(os.getenv("MODEL_6_RESEARCHER_KEY"), "Researcher", "meta/llama-3.1-8b-instruct"))
    
    print("\n--- Testing Tavily Round-Robin Keys ---")
    for i in range(1, 4):
        key = os.getenv(f"TAVILY_KEY_{i}")
        result = test_tavily(key, i)
        print(f"Tavily Key {i}: {result}")
        
    print("\n-------------------------------------------------\n")

if __name__ == "__main__":
    run_connection_tests()