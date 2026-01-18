# agent_a/agent_a.py
import os
import time
import uuid
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# agent_b는 컨테이너 DNS(agent_b:8000)로 가지 말고
# host.docker.internal:8000 으로 가야 Burp가 "외부로 나가는 트래픽"으로 잡기 쉬움
AGENT_B_URL = os.getenv("AGENT_B_URL", "http://host.docker.internal:8000/hello")

DEFAULT_PROMPT = os.getenv("PROMPT", "read file")

class AgentARequest(BaseModel):
    trace_id: str | None = None
    stage: str = "prompt"
    prompt: str = DEFAULT_PROMPT

@app.post("/agent")
def agent(req: AgentARequest):
    trace_id = req.trace_id or str(uuid.uuid4())

    payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": req.prompt,
    }

    # 프록시는 HTTP_PROXY/HTTPS_PROXY 환경변수로 자동 적용(requests 기본 trust_env=True)
    for i in range(30):
        try:
            r = requests.post(AGENT_B_URL, json=payload, timeout=3)
            return {
                "trace_id": trace_id,
                "stage": "agent_a_response",
                "agent_b": r.json(),
            }
        except requests.exceptions.RequestException:
            time.sleep(1)

    return {
        "trace_id": trace_id,
        "stage": "agent_a_response",
        "error": "failed to reach agent_b",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
