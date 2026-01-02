#docker-compose.yml 파일 만들기
compose 파일: 도커애플리케이션의 서비스, 네트워크, 볼륨 등의 설정을 yaml 형식으로 작성하는 파일
 구성 요소는 services: version: 등 다양함 (근데 version은 설정 따로 안 해도 됨)
 service: 여러 컨테이너 정의할 때 씀
   컨테이터 설정할 때 쓰는 키워드 중... build: 도커파일의 경로를 지정해서 빌드하기 (image를 사용하는 게 아니라)

<img width="576" height="932" alt="image" src="https://github.com/user-attachments/assets/773c0f8b-f4b5-4889-aeef-6cfd51de0f4b" />
- services: 에서 언급한 agent-net은 밑의 networks: 에서 정의한 이름!
- 그리고 bridge는 컨테이너들을 동일한 가상 LAN에 연결하는 리눅스 기반 가상 네트워크 스위치


