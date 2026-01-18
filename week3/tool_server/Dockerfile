FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn

COPY tool_server.py .

EXPOSE 5000

CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "5000"]
