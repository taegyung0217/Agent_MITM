from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/tool", methods=["POST"])
def tool():
    data = request.json

    print("\n[TOOL] 받은 요청:", data, flush=True)

    trace_id = data.get("trace_id", "no-trace")
    tool = data.get("tool")
    args = data.get("args", {})

    if tool == "read_file":
        path = args.get("path", "/data/hello.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                result = f.read()
        except Exception as e:
            return jsonify({
                "trace_id": trace_id,
                "tool": tool,
                "error": str(e)
            }), 500

    elif tool == "echo":
        result = args.get("text", "")

    else:
        return jsonify({
            "trace_id": trace_id,
            "tool": tool,
            "error": "unknown tool"
        }), 400

    response = {
        "trace_id": trace_id,
        "tool": tool,
        "result": result
    }

    print("[TOOL] 반환:", response, flush=True)

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)