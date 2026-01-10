## docker-compose.yml

```
tool_server:
    volumes:
      - ./data:/data
```

tool서버에서 /data/hello.txt 파일을 열려고 할 때, 실제로 있는지 미리 확인하는 용도

<img width="317" height="624" alt="image" src="https://github.com/user-attachments/assets/1d04119e-810e-4640-b71c-8a28b3fa816f" />

<br />

## Agent_A

os.getenv(): 운영체제(OS)에 설정된 환경변수 값을 읽어오는 함수
"Agent A의 입력을 컨테이너 실행 시 설정되는 값(예: 환경변수)으로 제한" 이라고 했다는 건,
컨테이너 실행 시 외부에서 주입하라는 의미 (에이전트 외부 입력 → 내부 처리의 경계를 명확히 볼 수 있음!)

근데!! 이건 내 컴퓨터의 os 기준이 아니라 도커 환경 기준이기 때문에 도커를 껐다가 다시 실행시키면 prompt값이 달라질 수 있음! 매번 같은 값이 아님.


<img width="201.75" height="170.75" alt="스크린샷 2026-01-05 221733" src="https://github.com/user-attachments/assets/a1ab910b-6044-41fc-b018-aee799a96ef9" />

<sub>일단 도움 안 받고 그냥 써보기...(최대한 작게 둬야지)</sub>

<br />

<img width="404" height="369" alt="image" src="https://github.com/user-attachments/assets/47c0aeef-5dce-461a-b0e1-b2264db13211" />

이게 최종

<br />

## Agent_B

agent_b.py에서

```
url = "http://tool_server:5000/tool"
```

는 Tool Server에게 보낼 때 쓰는 url

<br />

```
@app.post("/hello")
```

이건 b가 a에게 받은 url

<br />

```
if "file" in req.prompt: 
       tool_request = { 
           "trace_id": req.trace_id, 
           "stage": "prompt", 
           "prompt": req.prompt, 
       }
```

라고 썼었는데, B가 Tool Server에게 요청을 보낼 때는 A의 프롬프트를 전달하는 게 아니라 hello.txt파일을 읽기만 하면 되니까 args로 텍스트 파일 경로를 보내줘야 한다!

그러니까

```
if "file" in req.prompt:
        tool_request = {
            "trace_id": req.trace_id,
            "stage": "tool_call",
            "tool" : "read_file",
            "prompt": req.prompt,
            "args": {"path": "/data/hello.txt"},
        }
```

이렇게 고쳐주기

<br />

```
try:
         response = requests.post(url, json=tool_request, timeout=2)
         tool_result = response.json()
         print("Tool Server 응답: ", tool_result)
         break
```

여기서 response를 출력하는 게 아니라 response의 json을 출력

<br />

```
 print("그냥 echo")
    return {
        "trace_id": req.trace_id,
        "stage": req.stage,
        "response": f"Echo: {req.prompt}",
    }
```

이렇게 쓰면 stage에 agent_a에게 받았던 프롬프트대로 "prompt"가 출력되므로 ` req.stage `가 아니라 ` "response" `로 바꿔줘야 prompt -> tool_call -> tool_result -> response 흐름이 유지됨

<br />

<img width="365" height="363" alt="스크린샷 2026-01-10 130032" src="https://github.com/user-attachments/assets/82588a6a-ceb9-4d81-bc44-90e173562e64" />
<img width="367" height="109" alt="image" src="https://github.com/user-attachments/assets/1940b409-9463-4180-b597-78acd4563332" />


## Tool Server
Tool Server는 다른 서버에 요청을 보내는 게 아니니까 따로 URL이 필요 없음

```
path = req.args.get("path", "")
```
=> req.args 딕셔너리에서 "path"라는 키가 있으면 그 값을 가져오고
없으면 빈 문자열 ""을 쓸 거다.

<img width="314" height="389" alt="image" src="https://github.com/user-attachments/assets/b9ca533a-f68a-4a08-94d0-3d830a951ff3" />

<br />

## 컨테이너 만들기
이제 만든 파일들을 바타으로 컨테이너를 만든다.
docker-compose.yml 파일이 있는 (나는 week2 폴더) 위치에서 터미널을 열고 ` docker-compose up ` 실행행
