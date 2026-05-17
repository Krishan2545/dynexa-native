from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json

    prompt = data.get("prompt", "")

    import requests

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma:2b",
            "prompt": prompt,
            "stream": False
        }
    )

    ai_response = response.json()["response"]

    return jsonify({
        "original_prompt": prompt,
        "optimized_prompt": ai_response,
        "provider_selected": "gemma:2b"
    })

if __name__ == "__main__":
    app.run(port=5000)