FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*

# Flask와 Requests 설치
RUN pip install --no-cache-dir flask requests

COPY agent_b.py .

EXPOSE 8001

CMD ["python", "agent_b.py"]