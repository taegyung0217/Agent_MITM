from flask import Flask, request, jsonify

app = Flask(__name__)

# 모의 은행 DB
bankbooks = {
    "client": 10000,
    "adversary": 0
}

@app.route("/tool", methods=["POST"])
def tool():
    data = request.json
    print(f"\n[TOOL] Received: {data}", flush=True)

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