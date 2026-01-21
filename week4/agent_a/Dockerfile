FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests
COPY agent_a.py .
CMD ["python", "agent_a.py"]