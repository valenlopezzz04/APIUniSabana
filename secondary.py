from flask import Flask, jsonify, request
import random, time

app = Flask(__name__)

@app.get("/score")
def score():
    user = request.args.get("q", "unknown")
    time.sleep(0.05)
    return jsonify({
        "bureau": "secondary",
        "score": random.randint(300, 900),
        "query": user
    }), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
