import requests

# =========================
# REASONING ENGINE
# =========================

def generate_reasoning_response(prompt, context=""):

    final_prompt = f"""

You are Dynexa AI.

You are:
- practical
- concise
- intelligent
- helpful

Never say:
- you are DeepSeek
- you are Phi3
- you are TinyLlama

RECENT CONTEXT:
{context}

USER:
{prompt}

ASSISTANT:
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={
            "model": "phi3",
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 40
            }
        },

        timeout=60
    )

    return response.json()["response"].strip()