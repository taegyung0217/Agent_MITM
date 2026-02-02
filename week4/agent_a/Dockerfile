FROM python:3.12-slim

WORKDIR /app

# 네트워크 디버깅용 tcpdump 설치
RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir requests flask

# 파일명 일치 확인 (agent_a.py)
COPY agent_a.py .

EXPOSE 8002

CMD ["python", "agent_a.py"]