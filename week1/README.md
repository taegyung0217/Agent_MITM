## docker-compose.yml 파일 만들기
compose 파일: 도커애플리케이션의 서비스, 네트워크, 볼륨 등의 설정을 yaml 형식으로 작성하는 파일
 구성 요소는 services: version: 등 다양함 (근데 version은 설정 따로 안 해도 됨)
 service: 여러 컨테이너 정의할 때 씀
   컨테이터 설정할 때 쓰는 키워드 중... build: 도커파일의 경로를 지정해서 빌드하기 (image를 사용하는 게 아니라)

<img width="576" height="932" alt="image" src="https://github.com/user-attachments/assets/773c0f8b-f4b5-4889-aeef-6cfd51de0f4b" />
- services: 에서 언급한 agent-net은 밑의 networks: 에서 정의한 이름!
- 그리고 bridge는 컨테이너들을 동일한 가상 LAN에 연결하는 리눅스 기반 가상 네트워크 스위치

## Agent_a
- HTTP POST 요청 생성
- JSON 형태의 tool-call 메시지 전송
  -> client 역할!
agent_a 파일 구조
|agent_a/
|  Dockerfile
|  agent_a.py

### agent_a.py
<img width="1199" height="1063" alt="image" src="https://github.com/user-attachments/assets/81a32fe6-fc85-45b3-93ae-7b628291b48f" width="106" height="120"/>
- tool_call에서 각 key, value는 통신에서 자체저으로 의미를 갖는 건 아니고 수신자 쪽에서 if(tool == "read_file") 뭐 이런 식으로 쓰임!
  
### Dockerfile
<img width="751" height="479" alt="image" src="https://github.com/user-attachments/assets/33dc6d0a-218d-41fb-8f6c-f1d432637f25" width="150" height="96"/>
- From(파이썬 환경 준비): Python 3.11이 이미 설치된 리눅스 (slim한!!) 이미지 사용
- WORKDIR: 컨테이너 내부의 작업 디렉토리 설정하기 (cd /app랑 같은 의미)
- RUN: python 라이브러리인 requests 설치하기
- COPY: 로컬에 있는 agent_a.py를 컨테이너의 현재 디렉토리(/app)로 복사
- CMD: agent_a.py 실행

## Agent_b
- `/tool` 엔드포인트 제공
- JSON 요청 수신 후 응답 반환
  -> server 역할!

### agent_b.py
<img width="1033" height="988" alt="image" src="https://github.com/user-attachments/assets/e7fa0da7-169b-47a2-967b-9ef58b785d30" width="99" height="103" />
- app=FastAPI(): Agent B 서버 그 자체 -> /tool 엔드포인트를 제공 & Agent A의 POST 요청을 받음

### Dockerfile
<img width="1321" height="601" alt="image" src="https://github.com/user-attachments/assets/23469533-e1d3-4e17-9626-29191d2062a2" width="132" height="60" />
- RUN apt-get~ : 컨테이너 자체에서 캡처할 때 씀
- RUN pip install ~: FastAPI 실행에 필요한 최소 패키지 설치
- EXPOSE 8000: 그냥 8000번 포트를 쓴다는 안내일 뿐


## 컨테이너 만들기
1. 이미지 생성 (build) -> 2. 컨테이너 실행 (run)
-> docker compose up으로 한 번에 하기

### Windows PowerShell 1
Docker Desktop을 실행시킨 채로 프로젝트 파일에서 shell을 열어서
```
docker compose up --build (terminal 1)
```
를 입력하면 컨테이너가 만들어진다
<img width="2879" height="1651" alt="스크린샷 2026-01-03 002148" src="https://github.com/user-attachments/assets/ea23fc64-1721-4e21-a7df-6ca34514e1b7" />
<img width="2879" height="806" alt="스크린샷 2026-01-03 002219" src="https://github.com/user-attachments/assets/18ae3ecb-67e0-46b0-96df-ac454ebd7955" />

그리고 도커에 들어가 확인해보면
<img width="2367" height="692" alt="스크린샷 2026-01-03 002310" src="https://github.com/user-attachments/assets/f84e438a-957c-4a64-91e8-b0266e9a3ad5" />
만들어진 컨테이너와, 그 사이의 통신 트래픽이 기록돼 있다!!

### Windows PowerShell 2
첫 번째 shell과 도커를 끄지 않은 채로 새로운 shell을 열어서
```
docker compose exec agent_b tcpdump -i eth0 -s 0 -w /tmp/agent_http.pcap tcp port 8000
```
를 입력하면 (나는 agent_b, week1-agent_b, week1-agent_b-1 등 다 시도해도 해당 컨테이너가 없다고 하길래 compose를 추가해 이름이 굳이 필요 없도록 했다)

<img width="2879" height="164" alt="스크린샷 2026-01-03 003358" src="https://github.com/user-attachments/assets/81b6c8cf-7381-4622-a76a-934d7701f26e" />

간단한 경고문 뒤로, _tcpdump: listening on eht0, ..._ 패킷을 capture 중이라는 것을 알 수 있다!!

그리고 Ctrl + C를 눌러 종료하면 
<img width="617" height="113" alt="스크린샷 2026-01-03 003955" src="https://github.com/user-attachments/assets/de7533b9-90ed-4bd2-974e-ae161d0cd9a4" />

이렇게 총 몇 개의 패킷을 capture했는지에 대한 정보가 나온다!!

### Windows PowerShell 3
그리고 다시 새로운 shell을 열어 
```
docker compose restart agent_a
```
를 입력해 다시 
