## docker-compose.yml 파일 만들기
compose 파일: 도커애플리케이션의 서비스, 네트워크, 볼륨 등의 설정을 yaml 형식으로 작성하는 파일
 구성 요소는 services: version: 등 다양함 (근데 version은 설정 따로 안 해도 됨)
 service: 여러 컨테이너 정의할 때 씀
   컨테이터 설정할 때 쓰는 키워드 중... build: 도커파일의 경로를 지정해서 빌드하기 (image를 사용하는 게 아니라)

<img width="288" height="466" alt="image" src="https://github.com/user-attachments/assets/773c0f8b-f4b5-4889-aeef-6cfd51de0f4b"/>

- services: 에서 언급한 agent-net은 밑의 networks: 에서 정의한 이름!
- 그리고 bridge는 컨테이너들을 동일한 가상 LAN에 연결하는 리눅스 기반 가상 네트워크 스위치

<br />
<br />

## Agent_a
- HTTP POST 요청 생성
- JSON 형태의 tool-call 메시지 전송

   -> client 역할!

agent_a 파일 구조

|agent_a/

|    Dockerfile

|    agent_a.py


### agent_a.py
<img width="600" height="531" alt="image" src="https://github.com/user-attachments/assets/81a32fe6-fc85-45b3-93ae-7b628291b48f"/>

- tool_call에서 각 key, value는 통신에서 자체저으로 의미를 갖는 건 아니고 수신자 쪽에서 if(tool == "read_file") 뭐 이런 식으로 쓰임!
 

### Dockerfile
<img width="375" height="240" alt="image" src="https://github.com/user-attachments/assets/33dc6d0a-218d-41fb-8f6c-f1d432637f25"/>

- From(파이썬 환경 준비): Python 3.11이 이미 설치된 리눅스 (slim한!!) 이미지 사용
- WORKDIR: 컨테이너 내부의 작업 디렉토리 설정하기 (cd /app랑 같은 의미)
- RUN: python 라이브러리인 requests 설치하기
- COPY: 로컬에 있는 agent_a.py를 컨테이너의 현재 디렉토리(/app)로 복사
- CMD: agent_a.py 실행

<br />
<br />

## Agent_b
- `/tool` 엔드포인트 제공
- JSON 요청 수신 후 응답 반환

  -> server 역할!

### agent_b.py
<img width="516" height="494" alt="image" src="https://github.com/user-attachments/assets/e7fa0da7-169b-47a2-967b-9ef58b785d30" />

- app=FastAPI(): Agent B 서버 그 자체 -> /tool 엔드포인트를 제공 & Agent A의 POST 요청을 받음


### Dockerfile
<img width="660" height="300" alt="image" src="https://github.com/user-attachments/assets/23469533-e1d3-4e17-9626-29191d2062a2"/>

- RUN apt-get~ : 컨테이너 자체에서 캡처할 때 씀
- RUN pip install ~: FastAPI 실행에 필요한 최소 패키지 설치
- EXPOSE 8000: 그냥 8000번 포트를 쓴다는 안내일 뿐

<br />
<br />

## 컨테이너 만들기
1. 이미지 생성 (build) -> 2. 컨테이너 실행 (run)
-> docker compose up으로 한 번에 하기


### Windows PowerShell 1 (트래픽(로그) 확인)
Docker Desktop을 실행시킨 채로 프로젝트 파일에서 shell을 열어서
```
docker compose up --build (terminal 1)
```
를 입력하면 컨테이너가 만들어진다
<img width="1439" height="825" alt="스크린샷 2026-01-03 002148" src="https://github.com/user-attachments/assets/6c780e5b-9a8d-43b3-8b84-4e75de792708" />
<img width="1424" height="403" alt="스크린샷 2026-01-03 002219" src="https://github.com/user-attachments/assets/18ae3ecb-67e0-46b0-96df-ac454ebd7955" />
<br />
<br />
<br />
그리고 도커에 들어가 확인해보면
<img width="1183" height="346" alt="스크린샷 2026-01-03 002310" src="https://github.com/user-attachments/assets/f84e438a-957c-4a64-91e8-b0266e9a3ad5" />
만들어진 컨테이너와, 그 사이의 통신 트래픽이 기록돼 있다!!


### Windows PowerShell 2 (패킷 캡처)
첫 번째 shell과 도커를 끄지 않은 채로 새로운 shell을 열어서
```
docker compose exec agent_b tcpdump -i eth0 -s 0 -w /tmp/agent_http.pcap tcp port 8000
```
를 입력하면 (나는 agent_b, week1-agent_b, week1-agent_b-1 등 다 시도해도 해당 컨테이너가 없다고 하길래 compose를 추가해 이름이 굳이 필요 없도록 했다)

<img width="1439" height="82" alt="스크린샷 2026-01-03 003358" src="https://github.com/user-attachments/assets/bd539323-ecdb-45a2-b0b5-d5f6b6026062" />


간단한 경고문 뒤로, _tcpdump: listening on eht0, ..._ 패킷을 capture 중이라는 것을 알 수 있다!!


### Windows PowerShell 3 (트래픽을 발생시키기)
그리고 다시 새로운 shell을 열어 
```
docker compose restart agent_a
```
를 입력하면 Agent A가 다시 실행되고 -> POST /tool 발생하고,
지금 켜 둔 tcpdump가 이 패킷을 잡는 거다!!

그래서 다시 도커로 가서 살펴보면

<img width="1182" height="407" alt="스크린샷 2026-01-03 004728" src="https://github.com/user-attachments/assets/a23b440d-a3d0-4026-9718-1cbee6c17f4b" />

이렇게 트래픽이 추가돼있는 것을 볼 수 있다


### Windows PowerShell 2
다시 아까 두 번째 shell로 가서 
Ctrl + C를 눌러 종료하면 

<img width="308" height="56" alt="스크린샷 2026-01-03 003955" src="https://github.com/user-attachments/assets/de7533b9-90ed-4bd2-974e-ae161d0cd9a4" />

이렇게 총 몇 개의 패킷을 capture했는지에 대한 정보가 나온다!!
<br />
<br />
그리고
```
$cid = docker compose ps -q agent_b
docker cp ${cid}:/tmp/agent_http.pcap .\agent_http.pcap
```
를 입력해 캡처된 패킷 파일을 컨테이너에서 내 PC로 복사해준다 (아까처럼 컨테이너가 계속 존재하지 않다고 나오길래 이름을 변수에 저장해서 명령어를 실행했다)
패킷 캡처 자체는 이미 tcpdump가 끝냈고, 이건 결과물 회수 단계!!

<img width="1439" height="119" alt="스크린샷 2026-01-03 004435" src="https://github.com/user-attachments/assets/fc8b50c1-779f-45c6-85f7-a1e4ceeb128d" />


그러면 Successfully copied... 가 나온다

<br />
<br />

## Wireshark로 패킷 분석하기
만약 아까 캡처한 패킷들을 제대로 저장했다면 프로젝트 폴더에 
<img width="90" height="31" alt="image" src="https://github.com/user-attachments/assets/191e1018-b51f-462c-bb62-9ccf8233e6fc" />
이렇게 파일이 하나 저장되어 있을 것이다

이걸 wireshark에서 분석해보는 거다!

<img width="2879" height="1706" alt="image" src="https://github.com/user-attachments/assets/46415b86-42aa-4ccd-9177-21ad22e815e5" />

위의 Packet List는 패킷 한 줄 한 줄 POST /tool HTTP/1.1 같은 요약 정보를 보여주고,
아래 왼 쪽의 Packet Details는 TCP / HTTP / Header 구조를 사람이 읽기 좋게 해석된 결과를 보여주고,
아래 오른 쪽의 바이너리 같아 보이는 것들은 네트워크를 실제로 흐른 패킷의 원본 바이트(raw bytes)!

<br />
1-3번 패킷은 SYN -> SYN+ACK -> ACK로 TCP 연결을 맺는 3-way 과정
<img width="1149" height="445" alt="스크린샷 2026-01-03 122605" src="https://github.com/user-attachments/assets/547873c4-e674-4d20-b663-ccdbcf328f0f" />

이게 4번 패킷
- 총 266bytes가 캡처됨
- Src도 MAC, Dst도 MAC으로 EthernetII -> 같은 2계층 네트워크 (도커 브릿지를 썼으니까!!) 에서 통신함
- IPv4 (Src 172.18.0.3 → Dst 172.18.0.2): 도커 네트워크 내에서 A -> B의 IP로 전달됐다
- TCP (Src Port 51756 → Dst Port 8000, Len:200): 클라이언트의 포트에서 서버 포트로 데이터 전달 (Len:200은 이 TCP 패킷에 실린 페이로드 크기(HTTP 데이터 조각))

=> 즉 172.18.0.3가 -> 172.18.0.2에게 8000번 포트로, 200바이트 데이터를 보냈다

<br />
<br />

<img width="435" height="415" alt="image" src="https://github.com/user-attachments/assets/d63d5a9e-dbe5-4ba0-9ac8-039859fd933d" />
<img width="320" height="287" alt="image" src="https://github.com/user-attachments/assets/2d88448f-3d27-49aa-8abd-36c010085da7" />

이게 6번 패킷. 여기서부터 본격적인 http통신이 이뤄진다
- Protocol: HTTP/JSON
- Info: POST /tool HTTP/1.1, JSON (application/json)
- Hypertext Transfer Protocol (패킷 설명 맨 마지막 줄)
- JavaScript Object Notation: application/json(패킷 설명 맨 마지막 줄)
=>이 TCP 데이터는 HTTP 프로토콜 + 그 안에는 JSON payload
<br />

**IP 계층**

IPv4 Src: 172.18.0.3(agent_A) -> Dst: 172.18.0.2(agent_B)
<br />
<br />

**TCP 계층**

Src Port: 51756 (agent_A의 임시 포트)
Dst Port: 8000 (agent_B의 http 서버 포트)
Flags: PSH, ACK
TCP payload: 53 bytes
<br />
<br />

**TCP Reassembly**
```
[2 Reassembled TCP Segments (253 bytes): #4 (200), #6 (53)]
```
- HTTP 요청 전체는 253 bytes
- 그게 4번(200 bytes) + 6번(53 bytes) 로 나뉘어 전송됨
- Wireshark가 이걸 재조립해서 하나의 HTTP 요청으로 복원
=> TCP는 스트림 기반이라 요청이 쪼개져 올 수 있다는 걸 알 수 있음!!
<br />

**HTTP 계층**

<img width="368" height="232" alt="image" src="https://github.com/user-attachments/assets/4f29c58c-8e96-4b0c-b793-5e6a0c55ab1c" />
- POST /tool HTTP/1.1
- Content-Type: application/json
=> HTTP 메서드: POST, 엔드포인트: /tool, 데이터 형식: JSON
<br />

**JSON payload**

<img width="423" height="324" alt="image" src="https://github.com/user-attachments/assets/faf7f9ea-a2dc-4239-a805-a7ae5ce6dee9" />

여기서 내가 agnet_a 파이썬 코드에서 만들었던 tool_call을 확인할 수 있다!!
```
{
  "tool": "read_file",
  "args": {
    "path": "/hello.txt"
  }
}
```
