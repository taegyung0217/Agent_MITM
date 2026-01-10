from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class agentB_request_frame(BaseModel):
    trace_id: str
    stage: str
    tool: str
    args: dict


# Tool Server는 다른 서버에 요청을 보내는 게 아니니까 따로 URL이 필요 없음


@app.post("/tool")
def run_message(req: agentB_request_frame):
    if req.tool == "read_file":
        path = req.args.get("path", "")
        try:
            with open(path, "r") as f:
                file_content = f.read()
            return {
                "trace_id": req.trace_id,
                "stage": "tool_result",
                "result": file_content,
            }
        except Exception as e:
            return {
                "trace_id": req.trace_id,
                "stage": "tool_result",
                "error": str(e),
            }

    else:
        return {
            "trace_id": req.trace_id,
            "stage": "tool_result",
            "error": f"Unknown tool: {req.tool}",
        }
