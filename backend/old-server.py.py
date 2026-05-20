from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

# Simple in-memory cache
cache = {}

@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        start_time = time.time()

        data = request.json
        prompt = data.get("prompt", "").strip()

        # Empty prompt protection
        if not prompt:
            return jsonify({
                "error": "Prompt is empty"
            })

        # Check cache first
        if prompt in cache:
            return jsonify({
                "original_prompt": prompt,
                "optimized_prompt": cache[prompt],
                "provider_selected": "phi3:latest",
                "cached": True,
                "response_time": "instant"
            })

        # Better system prompt
        improved_prompt = f"""
You are an AI prompt optimizer.

Your task:
- Improve the user's prompt professionally
- Make it clearer
- Make it more effective for AI systems
- Keep it concise
- Remove unnecessary words
- Give only the improved prompt

User Prompt:
{prompt}
"""

        # Send to Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:latest",
                "prompt": improved_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 80
                }
            },
            timeout=60
        )

        result = response.json()

        ai_response = result.get("response", "No response generated")

        # Clean formatting
        cleaned_response = (
            ai_response
            .replace("**", "")
            .replace("*", "")
            .strip()
        )

        # Save to cache
        cache[prompt] = cleaned_response

        end_time = round(time.time() - start_time, 2)

        return jsonify({
            "original_prompt": prompt,
            "optimized_prompt": cleaned_response,
            "provider_selected": "phi3:latest",
            "cached": False,
            "response_time": f"{end_time}s"
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Model took too long to respond"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(port=5000)