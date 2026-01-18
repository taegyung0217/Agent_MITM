FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn requests

COPY agent_b.py .

EXPOSE 8000

CMD ["uvicorn", "agent_b:app", "--host", "0.0.0.0", "--port", "8000"]
