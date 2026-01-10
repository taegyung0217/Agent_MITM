FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY agent_a.py .

CMD ["python", "agent_a.py"]
