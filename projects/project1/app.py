from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Python App Deployed on AWS EC2 🚀</h1>
    <p>Hello from Flask running on Ubuntu EC2!</p>
    """

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)