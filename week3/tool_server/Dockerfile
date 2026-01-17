FROM python:3.10-slim

WORKDIR /app
COPY tool_server.py /app/tool_server.py

RUN pip install --no-cache-dir fastapi uvicorn

CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "8000"]