import requests

# =========================
# CODING ENGINE
# =========================

def generate_code_response(prompt):

    final_prompt = f"""

You are Dynexa Coding Engine.

Generate clean code.

USER:
{prompt}

ASSISTANT:
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={
            "model": "deepseek-coder:1.3b",
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 120
            }
        },

        timeout=90
    )

    return response.json()["response"].strip()