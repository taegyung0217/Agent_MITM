from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()

class ToolRequest(BaseModel):
    trace_id: str
    stage: str
    tool: str
    args: Dict[str, Any]

@app.post("/tool")
def run_tool(req: ToolRequest):
    # tool 서버는 '판단' 안 함: 요청대로만 실행 (과제용: 변조 확인에 최적)
    if req.tool == "read_file":
        path = str(req.args.get("path", ""))
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return {
                "trace_id": req.trace_id,
                "stage": "tool-response",
                "status": "ok",
                "tool": req.tool,
                "args": req.args,
                "result": {"content": content},
            }
        except Exception as e:
            return {
                "trace_id": req.trace_id,
                "stage": "tool-response",
                "status": "error",
                "tool": req.tool,
                "args": req.args,
                "error": str(e),
            }

    if req.tool == "echo":
        return {
            "trace_id": req.trace_id,
            "stage": "tool-response",
            "status": "ok",
            "tool": req.tool,
            "args": req.args,
            "result": {"content": str(req.args.get("message", ""))},
        }

    return {
        "trace_id": req.trace_id,
        "stage": "tool-response",
        "status": "error",
        "tool": req.tool,
        "args": req.args,
        "error": "unknown tool",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
