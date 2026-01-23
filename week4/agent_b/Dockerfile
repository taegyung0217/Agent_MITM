FROM python:3.12-slim

COPY CA.crt /usr/local/share/ca-certificates/burp_ca.crt
RUN update-ca-certificates

WORKDIR /app
RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask requests
COPY agent_b.py .
EXPOSE 8000
CMD ["python", "agent_b.py"]