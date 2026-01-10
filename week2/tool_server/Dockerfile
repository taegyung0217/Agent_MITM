FROM python:3.11-slim

RUN apt-get update && apt-get install -y tcpdump

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn

COPY tool_server.py .

EXPOSE 8000

CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "5000"]

