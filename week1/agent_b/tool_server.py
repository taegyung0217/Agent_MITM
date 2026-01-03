
#FastAPI는 http 서버 객체를 만들기 위한 클래스
from fastapi import FastAPI
#JSON 데이터를 “검증 + 구조화”하기 위한 클래스
from pydantic import BaseModel

#app=Flask(__name__)이랑 같은 역할
app = FastAPI()

#이 엔드포인트로 들어온 JSON 구조가 꼭 저래야 한다는 걸 명시
class ToolRequest(BaseModel):
    tool: str
    args: dict

#url이 꼭 /tool이고 POST 메서드로 들어온 요청만 처리
@app.post("/tool")
#요청이 ToolRequest 구조를 따라야만 함
def run_tool(req: ToolRequest):
    print("받은 요청:", req)
    return {
        "status": "ok",
        "tool": req.tool,
        "args": req.args
    }