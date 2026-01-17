FROM python:3.10-slim

WORKDIR /app
COPY agent_b.py /app/agent_b.py

RUN pip install --no-cache-dir fastapi uvicorn requests
RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*

# Python 버퍼링 비활성화
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "agent_b:app", "--host", "0.0.0.0", "--port", "8001"]