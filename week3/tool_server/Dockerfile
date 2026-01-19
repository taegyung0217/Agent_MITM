FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask requests
COPY tool_server.py .
EXPOSE 8001
CMD ["python", "tool_server.py"]