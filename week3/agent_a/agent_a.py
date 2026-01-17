import os
import time
import json
import uuid
import requests

AGENT_B_URL = os.getenv("AGENT_B_URL", "http://host.docker.internal:8001/agent")
PROMPT = os.getenv("PROMPT", "read a file")

# Burp Proxy 설정
PROXIES = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY"),
} if os.getenv("HTTP_PROXY") else None

def main():
    trace_id = str(uuid.uuid4())

    # 1) "prompt" 단계가 그대로 네트워크에 실리도록 JSON에 담아 전송
    payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": PROMPT,
    }

    print(f"[Agent A] Using proxy: {PROXIES}")

    # Agent B 준비 대기(week1 스타일로 재시도)
    for i in range(30):
        try:
            r = requests.post(AGENT_B_URL, json=payload, timeout=2, proxies=PROXIES)
            r.raise_for_status()
            break
        except Exception as e:
            print(f"[{i+1}/30] agent_b 준비 안 됨… 재시도 ({e})")
            time.sleep(1)
    else:
        raise RuntimeError("agent_b가 끝내 준비되지 않았음")

    # 2) Agent B가 반환한 "tool-call / response"를 그대로 출력
    resp = r.json()
    print("\n===== Agent A received (from Agent B) =====")
    print(json.dumps(resp, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()