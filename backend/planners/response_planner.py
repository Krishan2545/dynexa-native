import requests

# =========================
# LIGHTWEIGHT PLANNER
# =========================

def generate_execution_plan(user_prompt):

    planner_prompt = f"""

Classify the request briefly.

Return format:

TASK:
NEEDS_RETRIEVAL:
NEEDS_MEMORY:
TASK_TYPE:

USER:
{user_prompt}
"""

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={

                "model": "tinyllama",

                "prompt": planner_prompt,

                "stream": False,

                "options": {

                    "temperature": 0.1,

                    "num_predict": 40
                }
            },

            timeout=30
        )

        result = response.json()["response"].strip()

        return result

    except Exception as e:

        return f"Planner Error: {str(e)}"