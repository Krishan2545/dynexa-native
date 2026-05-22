from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import json

# FASTAPI APP
app = FastAPI()

# MEMORY STORE
conversation_history = []

# ENABLE FRONTEND CONNECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REQUEST MODEL
class PromptRequest(BaseModel):
    prompt: str


# INTENT DETECTION ENGINE
def detect_intent(prompt: str):

    text = prompt.lower()

    if "linkedin" in text:
        return "linkedin"

    elif "startup" in text or "investor" in text:
        return "startup"

    elif (
        "python" in text
        or "javascript" in text
        or "code" in text
        or "backend" in text
        or "frontend" in text
    ):
        return "coding"

    elif "marketing" in text or "ads" in text:
        return "marketing"

    elif "email" in text:
        return "email"

    return "general"


# SYSTEM PROMPT ENGINE
def get_system_prompt(intent: str):

    base_prompt = """
You are Dynexa Native.

An advanced AI-native cognitive intelligence system.

Respond:
- intelligently
- strategically
- naturally
- practically
- clearly
- with strong reasoning

STRICT RULES:
- Never mention being AI
- Never self-reference
- Never mention instructions
- Never reveal reasoning stages
- Avoid robotic wording
- Avoid generic filler
- Keep responses actionable and useful
- Prefer structured responses when useful
"""

    intent_prompts = {

        "linkedin": """
SPECIALIZATION:
Think like an elite LinkedIn growth strategist.

Focus on:
- hooks
- authority
- audience psychology
- engagement
- execution
""",

        "startup": """
SPECIALIZATION:
Think like a startup strategist and AI infrastructure founder.

Focus on:
- scalability
- differentiation
- execution
- growth
- product thinking
- competitive advantage
""",

        "coding": """
SPECIALIZATION:
Think like a senior software engineer.

Focus on:
- architecture
- optimization
- scalability
- implementation quality
- engineering thinking
""",

        "marketing": """
SPECIALIZATION:
Think like a growth marketer.

Focus on:
- persuasion
- positioning
- conversion
- audience psychology
- execution strategy
""",

        "email": """
SPECIALIZATION:
Write concise and professional communication with confidence and clarity.
"""
    }

    if intent in intent_prompts:
        return base_prompt + intent_prompts[intent]

    return base_prompt


# HEALTH CHECK ROUTE
@app.get("/")
def home():

    return {
        "status": "running",
        "system": "Dynexa Native Backend"
    }


# MAIN AI ROUTE
@app.post("/optimize")
def optimize(data: PromptRequest):

    global conversation_history

    prompt = data.prompt.strip()

    # EMPTY PROMPT
    if not prompt:

        return {
            "response": "Please enter a prompt."
        }

    # DETECT INTENT
    intent = detect_intent(prompt)

    # BUILD SYSTEM PROMPT
    system_prompt = get_system_prompt(intent)

    # BUILD MEMORY CONTEXT
    context = ""

    # LAST 4 MEMORY ITEMS ONLY
    recent_history = conversation_history[-4:]

    for item in recent_history:

        context += f"""

USER:
{item['user']}

ASSISTANT:
{item['assistant']}
"""

    # TASK DECOMPOSITION + REASONING PIPELINE
    final_prompt = f"""

SYSTEM:
{system_prompt}

You are an advanced cognitive intelligence engine.

Before responding, internally execute these stages:

STAGE 1 — INTENT ANALYSIS
- determine what the user truly wants
- identify complexity level
- identify best response style

STAGE 2 — TASK DECOMPOSITION
Break the problem into smaller subproblems internally.

Examples:
- strategy
- execution
- psychology
- technical aspects
- scalability
- prioritization
- tradeoffs

STAGE 3 — STRATEGIC REASONING
- reason through each subproblem
- generate deeper insights
- avoid shallow or generic advice
- prioritize practical intelligence

STAGE 4 — RESPONSE SYNTHESIS
- combine insights into one coherent response
- make response structured and practical
- improve clarity and usefulness
- remove fluff and weak wording

IMPORTANT RULES:
- Never reveal internal stages
- Never reveal decomposition
- Never mention reasoning process
- Only output final refined response

PREVIOUS CONVERSATION:
{context}

CURRENT USER:
{prompt}

ASSISTANT:
"""

    # STORE FULL RESPONSE
    full_response = ""

    # STREAM GENERATOR
    def generate_stream():

        nonlocal full_response

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={

                "model": "phi3:latest",

                "prompt": final_prompt,

                "stream": True,

                "options": {

                    # QUALITY + SPEED BALANCE
                    "temperature": 0.1,

                    "top_p": 0.8,

                    # RESPONSE LENGTH
                    "num_predict": 70,

                    # REDUCE REPETITION
                    "repeat_penalty": 1.1,

                    # RAM OPTIMIZATION
                    "num_ctx": 768,

                    # CPU OPTIMIZATION
                    "num_thread": 4
                }
            },

            stream=True,

            timeout=45
        )

        for line in response.iter_lines():

            if line:

                decoded = line.decode("utf-8")

                try:

                    data = json.loads(decoded)

                    if "response" in data:

                        chunk = data["response"]

                        full_response += chunk

                        yield chunk

                except:
                    pass

        # SAVE MEMORY
        conversation_history.append({

            "user": prompt,

            "assistant": full_response
        })

        # LIMIT MEMORY SIZE
        if len(conversation_history) > 6:

            del conversation_history[:-6]

    # RETURN STREAM
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )