import os
import time
import uuid
import requests
import urllib3

# 과제 설명과 동일
PROMPT = os.getenv("PROMPT", "read_file")
AGENT_B_URL = os.getenv("AGENT_B_URL", "http://127.0.0.1:8000/agent")

# Burp 프록시 On/Off 설정
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

# 프록시 안 사용 
PROXIES = None

# 프록시 사용 
if USE_PROXY:
    # 프록시 설정 (외부 통신용)
    PROXIES = {
        "http": "http://host.docker.internal:8080",
        "https": "http://host.docker.internal:8080",
    }

def main():
    # agent-b 서버가 준비될 때까지 대기
    time.sleep(3)
    
    trace_id = str(uuid.uuid4())

    payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": PROMPT,
    }

    print("[A] POST URL:", AGENT_B_URL, flush=True)
    print("[A] USE_PROXY:", USE_PROXY, flush=True)
    print("[A] PROXIES:", PROXIES, flush=True)
    print("[A] payload:", payload, flush=True)

    r = requests.post(
        AGENT_B_URL,
        json=payload,
        proxies=PROXIES,
        timeout=30,
    )

    print("[A] status:", r.status_code, flush=True)
    print("[A] content-type:", r.headers.get("Content-Type"), flush=True)
    print("[A] raw (first 300):", r.text[:300], flush=True)

    ct = r.headers.get("Content-Type", "") or ""
    if "application/json" in ct:
        print("[A] json:", r.json(), flush=True)
    else:
        print("[A] NOT JSON. (Burp/Upstream 설정 확인)", flush=True)


if __name__ == "__main__":
    main()