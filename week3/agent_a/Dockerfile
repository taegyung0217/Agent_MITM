FROM python:3.10-slim

WORKDIR /app
COPY agent_a.py /app/agent_a.py

RUN pip install --no-cache-dir requests

CMD ["python", "agent_a.py"]