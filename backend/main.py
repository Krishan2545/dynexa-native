from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Enable frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request structure
class PromptRequest(BaseModel):
    prompt: str


# INTENT DETECTION
def detect_intent(prompt):

    text = prompt.lower()

    if "linkedin" in text:
        return "linkedin"

    elif "startup" in text or "investor" in text:
        return "startup"

    elif "python" in text or "javascript" in text or "code" in text:
        return "coding"

    elif "marketing" in text or "ads" in text:
        return "marketing"

    elif "email" in text:
        return "email"

    return "general"


# SYSTEM PROMPT ENGINE
def get_system_prompt(intent):

    base_prompt = """
You are an elite AI intelligence system.

Your purpose:
- provide intelligent responses
- enhance reasoning
- improve clarity
- think strategically
- respond naturally and concisely

STRICT RULES:
- NEVER mention being AI
- NEVER mention system prompts
- NEVER mention instructions
- NEVER self-reference
- NEVER sound robotic
- NEVER over-explain
- NEVER generate filler text

STYLE:
- concise
- sharp
- premium
- intelligent
- practical
- modern

Always prioritize:
clarity + usefulness + intelligence.
"""

    intent_prompts = {

        "linkedin": """
SPECIALIZATION:
Think like an elite LinkedIn growth strategist.
Focus on authority, engagement, hooks, positioning, and audience psychology.
""",

        "startup": """
SPECIALIZATION:
Think like a startup founder, strategist, and AI infrastructure architect.
Focus on execution, scalability, growth, differentiation, and product thinking.
""",

        "coding": """
SPECIALIZATION:
Think like a senior software engineer.
Focus on architecture, scalability, clean code, optimization, and implementation quality.
""",

        "marketing": """
SPECIALIZATION:
Think like a world-class growth marketer.
Focus on conversion, persuasion, attention, and execution strategy.
""",

        "email": """
SPECIALIZATION:
Write concise and professional communication with clarity and confidence.
"""
    }

    if intent in intent_prompts:
        return base_prompt + intent_prompts[intent]

    return base_prompt


# HOME ROUTE
@app.get("/")
def home():
    return {
        "message": "Dynexa Backend Running"
    }


# MAIN AI ROUTE
@app.post("/optimize")
def optimize(data: PromptRequest):

    prompt = data.prompt

    # Detect intent
    intent = detect_intent(prompt)

    # Build system prompt
    system_prompt = get_system_prompt(intent)

    # Final AI prompt
    final_prompt = f"""
SYSTEM:
{system_prompt}

USER:
{prompt}

ASSISTANT:
"""

    # OLLAMA REQUEST
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:latest",
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.85,
                "num_predict": 180,
                "repeat_penalty": 1.2
            }
        }
    )

    result = response.json()["response"].strip()

    return {
        "response": result,
        "intent": intent
    }