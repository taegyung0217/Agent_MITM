# agent_b/agent_b.py
from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
import time

app = FastAPI()

class Message_frame(BaseModel):
    trace_id: str
    stage: str
    prompt: str

# tool_server도 컨테이너 DNS가 아니라 host 경유로(그래야 Burp history에 host.docker.internal:5000로 잡힘)
TOOL_URL = os.getenv("TOOL_URL", "http://host.docker.internal:5000/tool")

@app.post("/hello")
def run_message(req: Message_frame):
    if "file" in req.prompt:
        tool_request = {
            "trace_id": req.trace_id,
            "stage": "tool_call",
            "tool": "read_file",
            "args": {"path": "/data/hello.txt"},
        }

        for i in range(30):
            try:
                response = requests.post(TOOL_URL, json=tool_request, timeout=3)
                tool_result = response.json()
                break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            return {"trace_id": req.trace_id, "stage": "response", "error": "Tool Server unreachable"}

        return {
            "trace_id": req.trace_id,
            "stage": "response",
            "response": tool_result.get("result", str(tool_result)),
        }

    return {
        "trace_id": req.trace_id,
        "stage": "response",
        "response": f"Echo: {req.prompt}",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
