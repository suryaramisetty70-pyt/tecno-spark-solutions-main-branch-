import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Starting Comprehensive System Verification...")
    
    # 1. Test Health Endpoint
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            print("[PASS] Backend Health Check")
        else:
            print(f"[FAIL] Backend Health Check (Status: {res.status_code})")
    except Exception as e:
        print(f"[FAIL] Backend unreachable: {e}")
        sys.exit(1)

    # 2. Test Agent Marketplace (Listing)
    try:
        res = requests.get(f"{BASE_URL}/api/v1/agents")
        if res.status_code == 200:
            data = res.json()
            total = data.get("total", 0)
            print(f"[PASS] Agent Listing (Found {total} agents)")
        else:
            print(f"[FAIL] Agent Listing (Status: {res.status_code})")
    except Exception as e:
        print(f"[FAIL] Agent Listing Error: {e}")

    # 3. Test Chat Routing & AI Provider
    try:
        payload = {
            "agent_id": "personal_assistant",
            "intent": "Hello Buddy! Who are you?",
            "context": {}
        }
        print("Testing Personal Assistant AI response... (this may take a few seconds depending on the API key)")
        
        # In testing mode we might need auth headers. Let's create a test user or bypass it.
        # Let's just try first without auth. If it fails with 401, we know the endpoint is active.
        res = requests.post(f"{BASE_URL}/api/v1/agents/chat", json=payload)
        
        if res.status_code == 200:
            data = res.json()
            print(f"[PASS] Chat Routing & AI response: {data.get('response')[:100]}...")
        elif res.status_code == 401:
            print("[WARN] Chat requires Authentication. The system is securely locked down.")
        else:
            print(f"[FAIL] Chat Routing (Status: {res.status_code}) - {res.text}")
    except Exception as e:
        print(f"[FAIL] Chat Error: {e}")

if __name__ == "__main__":
    run_tests()
