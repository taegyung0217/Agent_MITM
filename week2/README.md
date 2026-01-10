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

## 컨테이너 만들기 (week1에서 이미 했던 내용!)

### terminal1
이제 만든 파일들을 바타으로 컨테이너를 만든다.
docker-compose.yml 파일이 있는 (나는 week2 폴더) 위치에서 터미널을 열고 ` docker compose up --build ` 실행
그러면 도커에 컨테이너가 week2라는 이름으로 만들어져있을 것이다!

### terminal2
어 뭐야

<img width="582" height="48.5" alt="스크린샷 2026-01-10 134843" src="https://github.com/user-attachments/assets/803cf52a-93d8-45c4-b99c-a7bbf1da26a7" />


agent_b 컨테이너가 없다고 한다.

<img width="719.75" height="48.75" alt="스크린샷 2026-01-10 135056" src="https://github.com/user-attachments/assets/1e0737cb-9ede-49d2-8d94-b9b16a0ff767" />

그래서 ` docker compose ps `로 확인해보니 tool_server만 돌아가고 있다.

<img width="2879" height="1614" alt="스크린샷 2026-01-10 135241" src="https://github.com/user-attachments/assets/b89ca461-3720-495b-8d71-88e11456c156" />

` docker compose logs agent_a `로 확인해보니 A는 B가 없어서 계속 연결을 실패한 모양이고, 

<img width="2879" height="629" alt="스크린샷 2026-01-10 140401" src="https://github.com/user-attachments/assets/f33b11a9-3817-4e56-bc4b-d78067256ca8" />

` docker compose logs agent_b `로 확인해보니 내가 requests를 설치 안 했나 보다.

허겁지겁 B의 Dockerfile에서 ` RUN pip install --no-cache-dir fastapi uvicorn requests `로 뒤에 requests를 추가해준다.

다시 빌드해주기...

<img width="500" height="306" alt="image" src="https://github.com/user-attachments/assets/dd48f776-4402-4182-8cc0-5f4bc5d185c8" />

아 뭔가 잘 된 것 같다.

<img width="2879" height="200" alt="스크린샷 2026-01-10 141401" src="https://github.com/user-attachments/assets/90612a55-55aa-4c8b-b5e8-4593f0e18fd5" />

<br />

(아 또 문제가 생김) tool_server의 Dockerfile에서 CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "5000"]로 바꿔줘야 포트끼리 잘 연결된다... 이것까지 바꿔주기...!

<img width="2879" height="270" alt="스크린샷 2026-01-10 143108" src="https://github.com/user-attachments/assets/a4992ea2-9d45-4e1a-a88c-7177f18664d5" />

포트번호 200으로 잘 나온다!!

이제 다 수습했으니 다시 ` docker compose exec agent_b tcpdump -i eth0 -s 0 -w /tmp/agent_http.pcap tcp port 8000 `로 패킷 캡처를 하자. 

### terminal3
` docker compose restart agent_a `로 트래픽 다시 발생싴키기

<img width="1974" height="453" alt="스크린샷 2026-01-10 143358" src="https://github.com/user-attachments/assets/5de36dfd-75a0-4b5a-a3fb-7545078c4813" />

그럼 도커에는 이렇게 기록된다!

### terminal2
이제 Ctrl + C를 눌러 종료하면 패킷 캡처 끝내기

### 패킷 캡처 마무리
<img width="2879" height="189" alt="스크린샷 2026-01-10 145234" src="https://github.com/user-attachments/assets/1b86a188-9298-4e3c-8ba4-7ef1c033d63f" />

<img width="2879" height="489" alt="스크린샷 2026-01-10 145003" src="https://github.com/user-attachments/assets/048a2a42-8ede-42a6-b3d3-f243a9d1923b" />

tcpdump 실행 -> restart agent_a -> ctrl+c로 캡처 중지
그러면 week2 폴더 아래에 pcap 파일이 하나 만들어져 있을 거다!

<br />

## WireShark



