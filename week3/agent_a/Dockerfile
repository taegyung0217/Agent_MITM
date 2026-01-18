FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn requests

COPY agent_a.py .

EXPOSE 8001

CMD ["uvicorn", "agent_a:app", "--host", "0.0.0.0", "--port", "8001"]
