import time
import requests

#A가 B에게 요청할 작업 내용 (JSON 문자열로 변환할 거니까 dict 형태)
tool_call = {
    "tool": "read_file",    #실행할 도구 이름
    "args": {"path": "/hello.txt"}  #도구 실행에 필요한 인자
}

url = "http://agent_b:8000/tool"


#30번까지 요청 시도
for i in range(30):
    try:
        response = requests.post(url, json=tool_call, timeout=2)
        #서버에서 받은 http 응답 body를 JSON으로 파싱해서 출력함!
        print("서버 응답: ", response.json())
        #성공하면 종료
        break
    except requests.exceptions.RequestException as e:
        print(f"[{i+1}/30] 서버 연결 실패!! 재시도 중... ")
        #1초 대기하고 재시도
        time.sleep(1)
else:
    raise RuntimeError("Agent B에 연결할 수 없음")