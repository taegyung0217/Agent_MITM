from flask import Flask, request, jsonify
import hmac
import hashlib
import json


app = Flask(__name__)
#agent_b와 공유하는 비밀키
SHARED_SECRET = b"my_bank_secret_key"

# 모의 은행 DB
bankbooks = {
    "client": 10000,
    "adversary": 0
}

@app.route("/tool", methods=["POST"])
def tool():
    data = request.json
    received_signature = request.headers.get("X-Signature")
    print(f"\n[TOOL] Received: {data}", flush=True)

    # 1. 받은 데이터로 다시 서명 계산
    payload_str = json.dumps(data, sort_keys=True)
    expected_signature = hmac.new(SHARED_SECRET, payload_str.encode(), hashlib.sha256).hexdigest()

    # 2. 서명 비교 (타이밍 공격 방지를 위해 compare_digest 사용)
    if not received_signature or not hmac.compare_digest(received_signature, expected_signature):
        print(f"[TOOL] ⚠️ 변조 감지! (Received: {received_signature})", flush=True)
        return jsonify({
            "trace_id": data.get("trace_id"),
            "result": "🚨 Error: Integrity Check Failed! Data Tampering Detected.",
            "debug_balance": bankbooks
        }), 403 # 거부(Forbidden) 응답

    # 3. 검증 통과 시 기존 로직 수행
    print(f"\n[TOOL] Integrity Verified. Processing: {data}", flush=True)


    tool = data.get("tool")
    args = data.get("args", {})
    trace_id = data.get("trace_id")
    result = ""

    if tool == "add_money":
        account = args.get("account")
        amount = args.get("amount", 0)
        if account in bankbooks:
            bankbooks[account] += amount
            result = f"Success. {account} balance: {bankbooks[account]}"
        else:
            result = "Account not found"

    elif tool == "subtract_money": # <- 출금 추가!
        account = args.get("account")
        amount = args.get("amount", 0)
        if account in bankbooks:
            bankbooks[account] -= amount # 여기서는 더하기가 아니라 뺍니다.
            result = f"Success. {account} balance: {bankbooks[account]}"
        else:
            result = "Account not found"

    
    elif tool == "echo":
        result = args.get("text", "")
    else:
        result = "Unknown tool"

    return jsonify({
        "trace_id": trace_id,
        "result": result,
        "debug_balance": bankbooks
    })

if __name__ == "__main__":
    # HTTPS 서버로 구동 (마운트된 인증서 사용)
    app.run(
        host="0.0.0.0", 
        port=8000, 
        ssl_context=('/app/server.crt', '/app/server.key')
    )