import requests
import time
import os
import uuid

AGENT_B_URL = os.getenv("AGENT_B_URL", "https://agent-b:8001/agent")
PROMPT = os.getenv("PROMPT", "deposit 5000 won")

def main():
    time.sleep(5) # 서버 부팅 대기
    
    payload = {
        "trace_id": str(uuid.uuid4()),
        "prompt": PROMPT
    }
    
    print(f"[A] Sending to {AGENT_B_URL}...", flush=True)
    
    try:
        # Agent B가 사설 인증서를 쓰므로 verify=False
        r = requests.post(AGENT_B_URL, json=payload, verify=False, timeout=30)
        print(f"[A] Result: {r.text}", flush=True)
    except Exception as e:
        print(f"[A] Error: {e}", flush=True)

if __name__ == "__main__":
    main()