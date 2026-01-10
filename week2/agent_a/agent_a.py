import os
import uuid
import time
import requests


#os.getenv(): 운영체제(OS)에 설정된 환경변수 값을 읽어오는 함수
#환경변수 PROMPT가 있으면 그 값을 사용하고, 환경변수 PROMPT가 없으면 "read file"을 대신 사용할 거임
PROMPT = os.getenv("PROMPT", "read file")

def main():
    #이번 실행(또는 이번 요청)을 대표하는 고유한 ID 하나 만들기
    trace_id = str(uuid.uuid4())

    # "prompt" 단계가 그대로 네트워크에 실리도록 (이번엔 PROMPT말고 다른 문자열로 대체)
    payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": "this is not a reading request",
    }
    url = "http://agent_b:8000/hello"

    for i in range(30):
        try:
            response = requests.post(url, json=payload, timeout=2)
            print("서버 응답: ", response.json())
            break
        except requests.exceptions.RequestException as e:
            print(f"[{i+1}/30] 서버 연결 실패!! 재시도 중... ")
            #1초 대기하고 재시도
            time.sleep(1)
    else:
        raise RuntimeError("Agent_b 서버에 연결할 수 없음")

#이 파일이 직접 실행된 경우에만 main()을 실행
if __name__ == "__main__":
    main()