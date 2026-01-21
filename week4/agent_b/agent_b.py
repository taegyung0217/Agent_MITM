from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOOL_URL = os.getenv("TOOL_URL", "http://127.0.0.1:8001/tool")

USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

PROXIES = None

if USE_PROXY:
    PROXIES = {
        "http": "http://host.docker.internal:8080",
        "https": "http://host.docker.internal:8080",
    }

print("[B] USE_PROXY:", USE_PROXY, flush=True)
print("[B] PROXIES:", PROXIES, flush=True)


@app.route("/agent", methods=["POST"])
def handle():
    data = request.get_json(force=True)

    print("\n[B] 받은 prompt:", data, flush=True)

    prompt = (data.get("prompt") or "")
    trace_id = data.get("trace_id", "no-trace")

    if "file" in prompt.lower():
        tool_name = "read_file"
        args = {"path": "/data/hello.txt"}
    else:
        tool_name = "echo"
        args = {"text": prompt}

    tool_call = {
        "trace_id": trace_id,
        "stage": "tool-call",
        "tool": tool_name,
        "args": args
    }

    print("[B] TOOL POST URL:", TOOL_URL, flush=True)
    print("[B] 생성된 tool-call:", tool_call, flush=True)
    print("[B] PROXIES:", PROXIES, flush=True)

    r = requests.post(
        TOOL_URL,
        json=tool_call,
        proxies=PROXIES,   # USE_PROXY가 참이면 Burp 경유
        timeout=30,
    )

    print("[B] Tool status:", r.status_code, flush=True)
    print("[B] Tool content-type:", r.headers.get("Content-Type"), flush=True)
    print("[B] Tool raw (first 200):", r.text[:200], flush=True)

    tool_result = r.json()

    response = {
        "trace_id": trace_id,
        "stage": "response",
        "tool_result": tool_result
    }

    print("[B] 최종 response:", response, flush=True)
    return jsonify(response)

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8000)
    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=("/certs/agent-b.crt", "/certs/agent-b.key")
    )