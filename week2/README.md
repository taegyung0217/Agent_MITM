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
` docker compose restart agent_a `로 트래픽 다시 발생시키기

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
<img width="1440" height="850" alt="image" src="https://github.com/user-attachments/assets/a460db22-769b-4095-be0c-d36548da29a1" />

아까 만들어진 pcap 파일을 업로드해 패킷을 살펴보면 위와 같다.
캡쳐된 패킷들 중, HTTP payload는 총 네 개이다.

<br />

HTTP 패킷 내에서 JSON필드는 다음과 같다.
<img width="720" height="425" alt="image" src="https://github.com/user-attachments/assets/72bf3495-8a31-490f-a3a4-24b3d3f90fb5" />
<img width="720" height="425" alt="image" src="https://github.com/user-attachments/assets/1a52c64b-70d1-4a36-8c8a-ef13ea6513ce" />
<img width="720" height="425" alt="image" src="https://github.com/user-attachments/assets/84998c21-814d-434a-9c20-5763a48dcd04" />
<img width="720" height="425" alt="image" src="https://github.com/user-attachments/assets/5b1227dd-35e8-432f-89f0-c1ad682e4bfe" />

IP를 보면, 172.20.0.2  /  172.20.0.3  /  172.20.0.4 로 3개가 등장하니 agent_a, agent_b, tool_server 인 것같다.
통신은 A -> B -> ("read_file"이면)tool_server -> B -> A일 테니,
172.20.0.4: agent_a
172.20.0.2: agent_b
172.20.0.3: tool_server
일 것이다.

### 패킷6
- agent_a가 외부로부터 받아온 payload인 trace_id, stage, prompt가 JSOM Object의 Member(JSON 필드)로 들어가나 보다.
- 그중 prompt는 PROMPT가 비어있어 default값인 "read file"로 전달됐다. (그럼 agent_b에서는 tool_server에게 파일을 읽을 것을 요청하겠다!!)

<br />

### 패킷14
- 이 패킷은 agent_b가 tool_server에게 보내는 tool-call이다.
- agent_a로부터 받은 payload인 req의 prompt 값에 "file"이라는 문자열이 있으니, if문으로 들어가 내가 썼던 코드대로 tool_request JSON이 전해졌다.
- 형태는 ` stage: tool_call, tool: read_file, args.path: /data/hello.txt `

<br />

### 패킷18
- tool_server가 HTTP 200 OK로 응답하는 패킷이다.
- 이 패킷은 tool_server가 file의 메시지를 읽고 난 결과를 return해 agent_b에게 보내는 패킷이다. 내가 hello.txt에 써놨던 메시지가 그대로 드러난다!!

<br />

### 패킷25
- agent_b가 agent_a에게 보내는 패킷이다.
- agent_a는 (내가 그렇게 코딩해둠) hello.txt 내용은 못 받고, agent_b가 tool_server로부터 읽은 메시지를 전달 받았든, 못 받았든 "Echo: {req.prompt}" 즉 agent_a가 payload에 담았던 "read file"을 echo로 받는다.
  
(어... 지금 생각해보면 @app.post("/tool")로 받은 결과를 써야 하는 건..가?)
(그래서 제출한 파일에는 "file" 문자열이 있는 경우에는 그 메시지를 agent_a까지도 받도록 수정해둠)

<br />

### 그 외
- 패킷 6 -> 14 -> 18 -> 25의 trace_id모두 같은데, 이건 하나의 요청 흐름이 네트워크 상태에서 이어진 모습을 보여준다!

<br />

## prompt 바꿔보기
agent_a가 agent_b에게 보내는 JSON에서 prompt 값을 바꾸어 agent_b가 tool-call을 부르지 않도록 해볼 거다.

agent_a.py에서 

```
payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": "this is not a reading request",
    }
```

payload에서 prompt값만 바꿔서 이번에는 tool-call을 안 보내게 했다.

<img width="1440" height="845" alt="image" src="https://github.com/user-attachments/assets/b8833d40-b192-4bb2-bf02-00cabe430db8" />

tool_server를 호출하지 않고, 바로 agent_b가 agent_a에게 답을 준다.

<br />


## +@) agent_a도 메시지를 받도록 수정한 결과
<img width="1440" height="737" alt="image" src="https://github.com/user-attachments/assets/f0d22b58-b7c8-4c6e-a9ba-69ac7cf91da1" />

<br />

## 단일 에이전트와 멀티 에이전트의 차이
- 단일 에이전트
    - 에이전트의 통신 과정이 하나의 프로세스 내부에서 수행
- 멀티 에이전트
    - 다수의 독립 프로세스에서 별도의 http 요청, JSON payload를 사용 (단일은 모두 내부에서 처리)
