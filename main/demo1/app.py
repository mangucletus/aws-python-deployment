from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Hello from Flask on AWS!"})

@app.route("/echo", methods=["POST"])
def echo():
    # Echo back whatever JSON was sent
    data = request.get_json(silent=True) or {}
    return jsonify({"you_sent": data})

@app.route("/health")
def health():
    # Used by the load balancer in Demo 2
    return "ok", 200

if __name__ == "__main__":
    # Bind to 0.0.0.0 so it is reachable from outside the machine
    app.run(host="0.0.0.0", port=8000)