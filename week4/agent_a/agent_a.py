from flask import Flask, request, render_template_string
import requests
import time
import os
import uuid

app = Flask(__name__)

AGENT_B_URL = os.getenv("AGENT_B_URL", "https://agent-b:8001/agent")
# PROMPT = os.getenv("PROMPT", "deposit 5000 won")

# 입출금 UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bank Deposit/Withdraw agent_a</title>
</head>
<body>
    <h2>💰 Agent A의 입출금 창구</h2>
    <form action="/send" method="post">
        금액: <input type="number" name="amount" value="5000">
        <button type="submit" name="action" value="deposit">입금</button>
        <button type="submit" name="action" value="withdraw">출금</button>
    </form>
    {% if result %}
    <hr>
    <h3>결과:</h3>
    <pre>{{ result }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/send", methods=["POST"])
def send():
    amount = int(request.form.get("amount", 0))
    action = request.form.get("action")

    prompt = f"{action} {amount} won"
    
    # time.sleep(5) # 서버 부팅 대기
    
    payload = {
        "trace_id": str(uuid.uuid4()),
        "prompt": prompt
    }
    
    print(f"[A] Sending to {AGENT_B_URL}...", flush=True)
    
    try:
        # Agent B가 사설 인증서를 쓰므로 verify=False
        r = requests.post(AGENT_B_URL, json=payload, verify=False, timeout=30)
        result = r.text
        print(f"[A] Result: {result}", flush=True)
    except Exception as e:
        print(f"[A] Error: {e}", flush=True)

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)