from flask import Flask, request, jsonify
import requests
import os
import hmac
import hashlib
import json


app = Flask(__name__)

# binary로 공유 비밀키 설정 (실제 환경에서는 환경변수나 안전한 곳에 보관)
SHARED_SECRET = b"my_bank_secret_key"

# 환경변수에서 가져오거나 기본값 설정
TOOL_URL = os.getenv("TOOL_URL", "https://tool-server:8000/tool")

# Burp Suite 프록시 설정 (Docker 내부에서 호스트의 Burp로 보냄)
PROXIES = {
    "http": "http://host.docker.internal:8080",
    "https": "http://host.docker.internal:8080",
}

# 마운트된 Burp 인증서 경로
BURP_CERT_PATH = "/usr/local/share/ca-certificates/burp.crt"

@app.route("/agent", methods=["POST"])
def handle():
    # 1. Agent A로부터 요청 받기
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").lower()
    trace_id = data.get("trace_id", "no-trace")
    
    print(f"[B] Received Prompt: {prompt}", flush=True)

    # 2. 의도 분석 및 Tool Call 생성 (시나리오 로직)
    if "deposit" in prompt:
        tool_name = "add_money"
        # 숫자만 추출 (예: "5000 won" -> 5000)
        amount = int(''.join(filter(str.isdigit, prompt)) or 0)
        args = {"account": "client", "amount": amount}
    elif "withdraw" in prompt:
        tool_name = "subtract_money"
        amount = int(''.join(filter(str.isdigit, prompt)) or 0)
        args = {"account": "client", "amount": amount}
        # args = {"path": "/data/hello.txt"}
    else:
        tool_name = "echo"
        args = {"text": prompt}

    tool_call = {
        "trace_id": trace_id,
        "tool": tool_name,
        "args": args
    }

    # print(f"[B] Sending to Tool Server (HTTPS via Burp): {TOOL_URL}", flush=True)
    
    
    # 2.5 HMAC 서명 생성
    # 데이터를 문자열로 변환 (순서 보장을 위해 sort_keys 사용)
    payload_str = json.dumps(tool_call, sort_keys=True)
    signature = hmac.new(SHARED_SECRET, payload_str.encode(), hashlib.sha256).hexdigest()

    print(f"[B] Generated Signature: {signature}", flush=True)


    # 3. Tool Server로 요청 (Burp Proxy 경유 + 인증서 검증) +@(헤더에 서명 추가)
    try:
        headers = {"X-Signature": signature} # 서명을 헤더에 담기
        
        r = requests.post(
            TOOL_URL,
            json=tool_call,
            headers=headers,
            proxies=PROXIES,  # 프록시 태우기
            verify=BURP_CERT_PATH,  # 마운트한 Burp 인증서로 검증
            timeout=180
        )
        tool_result = r.json()
    except Exception as e:
        print(f"[B] Error: {e}", flush=True)
        tool_result = {"error": str(e)}

    # 4. 결과 반환
    response = {
        "trace_id": trace_id,
        "tool_result": tool_result
    }
    return jsonify(response)

if __name__ == "__main__":
    # Agent B 자체도 HTTPS로 띄우고 싶다면 아래 ssl_context 주석 해제
    # app.run(host="0.0.0.0", port=8001, ssl_context=('/app/server.crt', '/app/server.key'))
    app.run(host="0.0.0.0", port=8001, ssl_context=('/app/server.crt', '/app/server.key'))