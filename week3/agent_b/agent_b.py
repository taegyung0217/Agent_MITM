from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import sys

# stdout 버퍼링 비활성화
sys.stdout.flush()

TOOL_URL = "http://host.docker.internal:8000/tool"


# Burp Proxy 설정
PROXIES = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY"),
} if os.getenv("HTTP_PROXY") else None

app = FastAPI()

# 시작 시 환경변수 출력
print("=" * 50, flush=True)
print(f"HTTP_PROXY: {os.getenv('HTTP_PROXY')}", flush=True)
print(f"HTTPS_PROXY: {os.getenv('HTTPS_PROXY')}", flush=True)
print(f"PROXIES: {PROXIES}", flush=True)
print("=" * 50, flush=True)

class AgentRequest(BaseModel):
    trace_id: str
    stage: str
    prompt: str

def decide_tool(prompt: str) -> dict:
    p = prompt.lower().strip()
    if "read" in p and "file" in p:
        return {
            "tool": "read_file",
            "args": {"path": "/data/hello.txt"}
        }
    return {
        "tool": "echo",
        "args": {"message": f"echo from Agent B (prompt='{prompt}')" }
    }

@app.post("/agent")
def agent_endpoint(req: AgentRequest):
    print(f"\n[Agent B] Received request: {req.prompt}", flush=True)
    print(f"[Agent B] Using proxy: {PROXIES}", flush=True)
    
    prompt = req.prompt
    tool_call = decide_tool(prompt)
    print(f"[Agent B] Decided tool: {tool_call}", flush=True)
    
    tool_payload = {
        "trace_id": req.trace_id,
        "stage": "tool-call",
        "tool": tool_call["tool"],
        "args": tool_call["args"],
    }

    print(f"[Agent B] Calling tool_server at {TOOL_URL}", flush=True)
    print(f"[Agent B] With proxies: {PROXIES}", flush=True)
    
    try:
        tool_resp = requests.post(TOOL_URL, json=tool_payload, timeout=3, proxies=PROXIES).json()
        print(f"[Agent B] Tool response received", flush=True)
    except Exception as e:
        print(f"[Agent B] ERROR calling tool_server: {e}", flush=True)
        raise

    response_payload = {
        "trace_id": req.trace_id,
        "stage": "response",
        "prompt_received": {
            "stage": req.stage,
            "prompt": req.prompt
        },
        "tool_call_sent": tool_payload,
        "tool_result_received": tool_resp,
        "final_response": {
            "text": f"Agent B processed prompt and executed tool '{tool_call['tool']}'."
        }
    }
    return response_payload