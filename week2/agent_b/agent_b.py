from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time

app = FastAPI()

class Message_frame(BaseModel):
    #아 키는 string이 아니구나
    trace_id: str
    stage: str
    prompt: str
    
# Tool 서버 주소
url = "http://tool_server:5000/tool"

@app.post("/hello")
def run_message(req: Message_frame):
    # "file"이라는 단어가 prompt에 포함되어 있을 때만 tool_server로 요청을 보냄
    if "file" in req.prompt:
        tool_request = {
            "trace_id": req.trace_id,
            "stage": "tool_call",
            "tool" : "read_file",
            "args": {"path": "/data/hello.txt"},
        }
        
        for i in range(30):
            try:
                response = requests.post(url, json=tool_request, timeout=2)
                tool_result = response.json()
                print("Tool Server 응답: ", tool_result)
                break
            except requests.exceptions.RequestException as e:
                print(f"[{i+1}/30] Tool Server 연결 실패!! 재시도 중... ")
                #1초 대기하고 재시도
                time.sleep(1)
        else:
            raise RuntimeError("Tool Server에 연결할 수 없음")

        return {
            "trace_id": req.trace_id,
            "stage": "response",
            "response": tool_result.get("result", str(tool_result)),
        }
    
    print("그냥 echo")
    return {
        "trace_id": req.trace_id,
        "stage": "response",
        "response": f"Echo: {req.prompt}",
    }
